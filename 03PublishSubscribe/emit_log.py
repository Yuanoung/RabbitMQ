#!/usr/bin/env python
# coding: utf-8
import pika
import sys

"""
在上篇教程中，我们搭建了一个工作队列，每个任务只分发给一个工作者（worker）。
在本篇教程中，我们要做的跟之前完全不一样 —— 分发一个消息给多个消费者（consumers）。
这种模式被称为“发布／订阅”。

为了描述这种模式，我们将会构建一个简单的日志系统。
它包括两个程序——第一个程序负责发送日志消息，第二个程序负责获取消息并输出内容。
在我们的这个日志系统中，所有正在运行的接收方程序都会接受消息。
我们用其中一个接收者（receiver）把日志写入硬盘中，另外一个接受者（receiver）把日志输出到屏幕上。
最终，日志消息被广播给所有的接受者（receivers）。
"""
connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

"""
交换机（Exchanges）
前面的教程中，我们发送消息到队列并从中取出消息。现在是时候介绍RabbitMQ中完整的消息模型了。
让我们简单的概括一下之前的教程：
    发布者（producer）是发布消息的应用程序。
    队列（queue）用于消息存储的缓冲。
    消费者（consumer）是接收消息的应用程序。
RabbitMQ消息模型的核心理念是：发布者（producer）不会直接发送任何消息给队列。
事实上，发布者（producer）甚至不知道消息是否已经被投递到队列。
发布者（producer）只需要把消息发送给一个交换机（exchange）。
交换机非常简单，它一边从发布者方接收消息，一边把消息推送到队列。
交换机必须知道如何处理它接收到的消息，是应该推送到指定的队列还是是多个队列，或者是直接忽略消息。
这些规则是通过交换机类型（exchange type）来定义的。

有几个可供选择的交换机类型：
    直连交换机（direct）, 主题交换机（topic）, （头交换机）headers和 扇型交换机（fanout）。
我们在这里主要说明最后一个 —— 扇型交换机（fanout）。先创建一个fanout类型的交换机，命名为logs：

扇型交换机（fanout）很简单，你可能从名字上就能猜测出来，它把消息发送给它所知道的所有队列。
这正是我们的日志系统所需要的。

交换器列表
rabbitmqctl能够列出服务器上所有的交换器：
    `sudo rabbitmqctl list_exchanges`
这个列表中有一些叫做amq.*的交换器。这些都是默认创建的，不过这时候你还不需要使用他们。

匿名的交换器
前面的教程中我们对交换机一无所知，但仍然能够发送消息到队列中。因为我们使用了命名为空字符串("")默认的交换机。
回想我们之前是如何发布一则消息：
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=message)
exchange参数就是交换机的名称。空字符串代表默认或者匿名交换机：消息将会根据指定的routing_key分发到指定的队列。
"""
channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')

message = ' '.join(sys.argv[1:]) or "info: Hello World!"

# 现在，我们就可以发送消息到一个具名交换机了, routing_key为空字符串：
channel.basic_publish(exchange='logs',
                      routing_key='',
                      body=message)
print(" [x] Sent %r" % (message,))
connection.close()
