#!/usr/bin/env python
# coding: utf-8
import pika
import sys

"""
在前面的教程中，我们实现了一个简单的日志系统。可以把日志消息广播给多个接收者。
本篇教程中我们打算新增一个功能 —— 使得它能够只订阅消息的一个字集。
例如，我们只需要把严重的错误日志信息写入日志文件（存储到磁盘），但同时仍然把所有的日志信息输出到控制台中
"""
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))
channel = connection.channel()

"""
直连交换机（Direct exchange）
我们的日志系统广播所有的消息给所有的消费者（consumers）。
我们打算扩展它，使其基于日志的严重程度进行消息过滤。
例如我们也许只是希望将比较严重的错误（error）日志写入磁盘，以免在警告（warning）或者信息（info）日志上浪费磁盘空间。
我们使用的扇型交换机（fanout exchange）没有足够的灵活性 —— 它能做的仅仅是广播。
我们将会使用直连交换机（direct exchange）来代替。
路由的算法很简单 —— 交换机将会对绑定键（binding key）和路由键（routing key）进行精确匹配，从而确定消息该分发到哪个队列。
在这个场景中，我们可以看到直连交换机 X和两个队列进行了绑定。
第一个队列使用orange作为绑定键;第二个队列有两个绑定，一个使用black作为绑定键，另外一个使用green。
这样以来，当路由键为orange的消息发布到交换机，就会被路由到队列Q1。
路由键为black或者green的消息就会路由到Q2。其他的所有消息都将会被丢弃。

多个绑定（Multiple bindings）
多个队列使用相同的绑定键是合法的。
这个例子中，我们可以添加一个X和Q1之间的绑定，使用black绑定键。
这样一来，直连交换机就和扇型交换机的行为一样，会将消息广播到所有匹配的队列。
带有black路由键的消息会同时发送到Q1和Q2。
"""
channel.exchange_declare(exchange='direct_logs',
                         exchange_type='direct')

"""
我们将会发送消息到一个直连交换机，把日志级别作为路由键。
这样接收日志的脚本就可以根据严重级别来选择它想要处理的日志。
我们先看看发送日志。
我们先假设“severity”的值是info、warning、error中的一个。
"""
severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(exchange='direct_logs',
                      routing_key=severity,
                      body=message)
print(sys.argv)
print(" [x] Sent %r:%r" % (severity, message))
connection.close()
