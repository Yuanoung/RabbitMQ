#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')

"""
临时队列
你还记得之前我们使用的队列名吗（ hello和task_queue）？
给一个队列命名是很重要的——我们需要把工作者（workers）指向正确的队列。
如果你打算在发布者（producers）和消费者（consumers）之间共享同队列的话，给队列命名是十分重要的。
但是这并不适用于我们的日志系统。我们打算接收所有的日志消息，而不仅仅是一小部分。
我们关心的是最新的消息而不是旧的。
为了解决这个问题，我们需要做两件事情。
首先，当我们连接上RabbitMQ的时候，我们需要一个全新的、空的队列。
我们可以手动创建一个随机的队列名，或者让服务器为我们选择一个随机的队列名（推荐）。
我们只需要在调用queue_declare方法的时候，不提供queue参数就可以了.
这时候我们可以通过result.method.queue获得已经生成的随机队列名。
它可能是这样子的：amq.gen-U0srCoW8TsaXjNh73pnVAw==。
第二步，当与消费者（consumer）断开连接的时候，这个队列应当被立即删除。exclusive标识符即可达到此目的。
"""
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

"""
我们已经创建了一个扇型交换机（fanout）和一个队列。
现在我们需要告诉交换机如何发送消息给我们的队列。
交换器和队列之间的联系我们称之为绑定（binding）。
现在，logs交换机将会把消息添加到我们的队列中。
绑定（binding）列表
你可以使用`rabbitmqctl list_bindings`列出所有现存的绑定。
"""
channel.queue_bind(exchange='logs',
                   queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r" % (body,))


channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
