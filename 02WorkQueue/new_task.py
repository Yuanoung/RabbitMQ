#!/usr/bin/env python
import pika
import sys
"""
在这篇教程中，我们将创建一个工作队列（Work Queue），它会发送一些耗时的任务给多个工作者（Worker）。
工作队列（又称：任务队列——Task Queues）是为了避免等待一些占用大量资源、时间的操作。
当我们把任务（Task）当作消息发送到队列中，一个运行在后台的工作者（worker）进程就会取出任务然后处理。
当你运行多个工作者（workers），任务就会在它们之间共享。
这个概念在网络应用中是非常有用的，它可以在短暂的HTTP请求中处理一些复杂的任务。

之前的教程中，我们发送了一个包含“Hello World!”的字符串消息。现在，我们将发送一些字符串，把这些字符串当作复杂的任务。
我们没有真实的例子，例如图片缩放、pdf文件转换。所以使用time.sleep()函数来模拟这种情况。
我们在字符串中加上点号（.）来表示任务的复杂程度，一个点（.）将会耗时1秒钟。比如"Hello..."就会耗时3秒钟。
我们对之前教程的send.py做些简单的调整，以便可以发送随意的消息。这个程序会按照计划发送任务到我们的工作队列中。
我们把它命名为new_task.py：
"""

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

"""
如果你没有特意告诉RabbitMQ，那么在它退出或者崩溃的时候，将会丢失所有队列和消息。
为了确保信息不会丢失，有两个事情是需要注意的：我们必须把“队列”和“消息”设为持久化。
首先，为了不让队列消失，需要把队列声明为持久化（durable=True）.

尽管这行代码本身是正确的，但是仍然不会正确运行。因为我们已经定义过一个叫hello的非持久化队列。
RabbitMq不允许你使用不同的参数重新定义一个队列，它会返回一个错误。
但我们现在使用一个快捷的解决方法——用不同的名字，例如task_queue。
另外，我们需要把我们的消息也要设为持久化——将delivery_mode的属性设为2。

注意：消息持久化
将消息设为持久化并不能完全保证不会丢失。
以上代码只是告诉了RabbitMq要把消息存到硬盘，但从RabbitMq收到消息到保存之间还是有一个很小的间隔时间。
因为RabbitMq并不是所有的消息都使用fsync(2)——它有可能只是保存到缓存中，并不一定会写到硬盘中。
并不能保证真正的持久化，但已经足够应付我们的简单工作队列。如果你一定要保证持久化，你需要改写你的代码来支持事务（transaction）。
"""
channel.queue_declare(queue='task_queue', durable=True)

message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                          delivery_mode=2,  # make message persistent
                      ))
print(" [x] Sent %r" % (message,))
connection.close()
