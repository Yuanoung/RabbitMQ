#!/usr/bin/env python
# coding: utf-8
import pika
"""
当客户端启动的时候，它创建一个匿名独享的回调队列。在RPC请求中，客户端发送带有两个属性的消息：一个是设置回调队列的 
reply_to 属性，另一个是设置唯一值的 correlation_id 属性。将请求发送到一个 rpc_queue 队列中。RPC工作者（又名：
服务器）等待请求发送到这个队列中来。当请求出现的时候，它执行他的工作并且将带有执行结果的消息发送给reply_to字段指定
的队列。客户端等待回调队列里的数据。当有消息出现的时候，它会检查correlation_id属性。如果此属性的值与请求匹配，将
它返回给应用。
"""
# 像往常一样，我们建立连接，声明队列
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='rpc_queue')


def fib(n):
    """我们声明我们的fibonacci函数，它假设只有合法的正整数当作输入。"""
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def on_request(ch, method, props, body):
    """我们为 basic_consume 声明了一个回调函数，这是RPC服务器端的核心。它执行实际的操作并且作出响应。"""
    n = int(body)

    print(" [.] fib(%s)" % (n,))
    response = fib(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


# 或许我们希望能在服务器上多开几个线程。为了能将负载平均地分摊到多个服务器，我们需要将 prefetch_count 设置好。
channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='rpc_queue')

print(" [x] Awaiting RPC requests")
channel.start_consuming()
