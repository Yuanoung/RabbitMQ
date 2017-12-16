#!/usr/bin/env python
# coding: utf-8
import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs',
                         exchange_type='direct')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

severities = sys.argv[1:]
if not severities:
    sys.stderr.print("Usage: %s [info] [warning] [error]" % (sys.argv[0],))
    sys.exit(1)

"""
绑定（binding）是指交换机（exchange）和队列（queue）的关系。
可以简单理解为：这个队列（queue）对这个交换机（exchange）的消息感兴趣。
绑定的时候可以带上一个额外的routing_key参数。
为了避免与basic_publish的参数混淆，我们把它叫做绑定键（binding key）。
以下是如何创建一个带绑定键的绑定。
绑定键的意义取决于交换机（exchange）的类型。
我们之前使用过的扇型交换机（fanout exchanges）会忽略这个值。
"""
for severity in severities:
    print(severity)
    channel.queue_bind(exchange='direct_logs',
                       queue=queue_name,
                       routing_key=severity)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body,))


channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
