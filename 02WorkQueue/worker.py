#!/usr/bin/env python
import pika
import time

"""
我们的旧脚本（receive.py）同样需要做一些改动：它需要为消息体中每一个点号（.）模拟1秒钟的操作。
它会从队列中获取消息并执行，我们把它命名为worker.py：
"""
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

"""
当处理一个比较耗时得任务的时候，你也许想知道消费者（consumers）是否运行到一半就挂掉。
当前的代码中，当消息被RabbitMQ发送给消费者（consumers）之后，马上就会在内存中移除。
这种情况，你只要把一个工作者（worker）停止，正在处理的消息就会丢失。同时，所有发送到这个工作者的还没有处理的消息都会丢失。
我们不想丢失任何任务消息。如果一个工作者（worker）挂掉了，我们希望任务会重新发送给其他的工作者（worker）。
为了防止消息丢失，RabbitMQ提供了消息响应（acknowledgments）。
消费者会通过一个ack（响应），告诉RabbitMQ已经收到并处理了某条消息，然后RabbitMQ就会释放并删除这条消息。
如果消费者（consumer）挂掉了，没有发送响应，RabbitMQ就会认为消息没有被完全处理，然后重新发送给其他消费者（consumer）。
这样，及时工作者（workers）偶尔的挂掉，也不会丢失消息。
消息是没有超时这个概念的；当工作者与它断开连的时候，RabbitMQ会重新发送消息。
这样在处理一个耗时非常长的消息任务的时候就不会出问题了。
消息响应默认是开启的。之前的例子中我们可以使用no_ack=True标识把它关闭。
是时候移除这个标识了，当工作者（worker）完成了任务，就发送一个响应。

忘记确认:
一个很容易犯的错误就是忘了basic_ack，后果很严重。
消息在你的程序退出之后就会重新发送，如果它不能够释放没响应的消息，RabbitMQ就会占用越来越多的内存。
为了排除这种错误，你可以使用rabbitmqctl命令，输出messages_unacknowledged字段：
$ sudo rabbitmqctl list_queues name messages_ready messages_unacknowledged
"""


def callback(ch, method, properties, body):
    print(" [x] Received %r" % (body,))
    time.sleep(body.count('.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


"""
公平调度
你应该已经发现，它仍旧没有按照我们期望的那样进行分发。
比如有两个工作者（workers），处理奇数消息的比较繁忙，处理偶数消息的比较轻松。然而RabbitMQ并不知道这些，它仍然一如既往的派发消息。
这时因为RabbitMQ只管分发进入队列的消息，不会关心有多少消费者（consumer）没有作出响应。它盲目的把第n-th条消息发给第n-th个消费者。

我们可以使用basic.qos方法，并设置prefetch_count=1。
这样是告诉RabbitMQ，再同一时刻，不要发送超过1条消息给一个工作者（worker），直到它已经处理了上一条消息并且作出了响应。
这样，RabbitMQ就会把消息分发给下一个空闲的工作者（worker）。

关于队列大小
如果所有的工作者都处理繁忙状态，你的队列就会被填满。你需要留意这个问题，要么添加更多的工作者（workers），要么使用其他策略。
"""
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='task_queue')

channel.start_consuming()
