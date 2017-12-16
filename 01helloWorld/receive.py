#!/usr/bin/env python
# coding:utf-8
import pika

"""
我们的第二个程序receive.py，将会从队列中获取消息并将其打印到屏幕上。
这次我们还是需要要先连接到RabbitMQ服务器。连接服务器的代码和之前是一样的。
"""
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

"""
下一步也和之前一样，我们需要确认队列是存在的。
我们可以多次使用queue_declare命令来创建同一个队列，但是只有一个队列会被真正的创建。

你也许要问: 为什么要重复声明队列呢 —— 我们已经在前面的代码中声明过它了。
如果我们确定了队列是已经存在的，那么我们可以不这么做，比如此前预先运行了send.py程序。
可是我们并不确定哪个程序会首先运行。这种情况下，在程序中重复将队列重复声明一下是种值得推荐的做法。

列出所有队列:
你也许希望查看RabbitMQ中有哪些队列、有多少消息在队列中。
此时你可以使用rabbitmqctl工具（使用有权限的用户）：
    `sudo rabbitmqctl list_queues`
（在Windows中不需要sudo命令）
    `rabbitmqctl list_queues`
"""
channel.queue_declare(queue='hello')

"""
从队列中获取消息相对来说稍显复杂。
需要为队列定义一个回调（callback）函数。
当我们获取到消息的时候，Pika库就会调用此回调函数。
这个回调函数会将接收到的消息内容输出到屏幕上。
"""


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


# 下一步，我们需要告诉RabbitMQ这个回调函数将会从名为"hello"的队列中接收消息：
channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

"""
要成功运行这些命令，我们必须保证队列是存在的，我们的确可以确保它的存在——因为我们之前已经使用queue_declare将其声明过了。
no_ack参数稍后会进行介绍。
最后，我们运行一个用来等待消息数据并且在需要的时候运行回调函数的无限循环。
"""
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
