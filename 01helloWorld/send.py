#!/usr/bin/env python
# coding:utf-8
import pika

"""
我们第一个程序send.py会发送一个消息到队列中。
首先要做的事情就是建立一个到RabbitMQ服务器的连接。
"""
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

"""
现在我们已经跟本地机器的代理建立了连接。如果你想连接到其他机器的代理上，需要把代表本地的localhost改为指定的名字或IP地址。
接下来，在发送消息之前，我们需要确认服务于消费者的队列已经存在。如果将消息发送给一个不存在的队列，RabbitMQ会将消息丢弃掉。
下面我们创建一个名为"hello"的队列用来将消息投递进去。
"""
channel.queue_declare(queue='hello')

"""
在RabbitMQ中，消息是不能直接发送到队列中的，这个过程需要通过交换机（exchange）来进行。
但是为了不让细节拖累我们的进度，这里我们只需要知道如何使用由空字符串表示的默认交换机即可。
如果你想要详细了解交换机，可以查看我们教程的第三部分来获取更多细节。默认交换机比较特别，
它允许我们指定消息究竟需要投递到哪个具体的队列中，队列名字需要在routing_key参数中指定。
"""
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")

"""
在退出程序之前，我们需要确认网络缓冲已经被刷写、消息已经投递到RabbitMQ。通过安全关闭连接可以做到这一点。
"""
connection.close()

"""
发送不成功！

如果这是你第一次使用RabbitMQ，并且没有看到“Sent”消息出现在屏幕上，你可能会抓耳挠腮不知所以。
这也许是因为没有足够的磁盘空间给代理使用所造成的（代理默认需要200MB的空闲空间），所以它才会拒绝接收消息。
查看一下代理的日志文件进行确认，如果需要的话也可以减少限制。配置文件文档会告诉你如何更改磁盘空间限制（disk_free_limit）。
"""