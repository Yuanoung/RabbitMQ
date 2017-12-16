#!/usr/bin/env python
# coding: utf-8
import sys
import pika
import uuid


class FibonacciRpcClient(object):
    """
    消息属性
    AMQP协议给消息预定义了一系列的14个属性。大多数属性很少会用到，除了以下几个：
        1. delivery_mode（投递模式）：将消息标记为持久的（值为2）或暂存的（除了2之外的其他任何值）。
           第二篇教程里接触过这个属性，记得吧？
        2. content_type（内容类型）:用来描述编码的mime-type。
           例如在实际使用中常常使用application/json来描述JOSN编码类型。
        3. reply_to（回复目标）：通常用来命名回调队列。
        4. correlation_id（关联标识）：用来将RPC的响应和请求关联起来。

    关联标识
    上边介绍的方法中，我们建议给每一个RPC请求新建一个回调队列。
    这不是一个高效的做法，幸好这儿有一个更好的办法 —— 我们可以为每个客户端只建立一个独立的回调队列。

    这就带来一个新问题，当此队列接收到一个响应的时候它无法辨别出这个响应是属于哪个请求的。
    correlation_id 就是为了解决这个问题而来的。我们给每个请求设置一个独一无二的值。
    稍后，当我们从回调队列中接收到一个消息的时候，我们就可以查看这条属性从而将响应和请求匹配起来。
    如果我们接手到的消息的correlation_id是未知的，那就直接销毁掉它，因为它不属于我们的任何一条请求。

    你也许会问，为什么我们接收到未知消息的时候不抛出一个错误，而是要将它忽略掉？
    这是为了解决服务器端有可能发生的竞争情况。尽管可能性不大，但RPC服务器还是有可能在已将应答发送给我们但还
    未将确认消息发送给请求的情况下死掉。如果这种情况发生，RPC在重启后会重新处理请求。这就是为什么我们必须在
    客户端优雅的处理重复响应，同时RPC也需要尽可能保持幂等性。
    """

    def __init__(self):
        """建立连接、通道并且为回复（replies）声明独享的回调队列"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        # 订阅这个回调队列，以便接收RPC的响应
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        """`on_response`回调函数对每一个响应执行一个非常简单的操作，
        检查每一个响应消息的`correlation_id`属性是否与我们期待的一致，
        如果一致，将响应结果赋给`self.response`，然后跳出`consuming`循环。
        """
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        """定义我们的主要方法 call 方法。它执行真正的RPC请求"""
        self.response = None
        # 首先我们生成一个唯一的 correlation_id 值并且保存起来，'on_response'回调函数会用它来获取符合要求的响应。
        self.corr_id = str(uuid.uuid4())
        # 我们将带有 reply_to 和 correlation_id 属性的消息发布出去
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(n))
        while self.response is None:
            # 等待正确的响应到来
            self.connection.process_data_events()
        return int(self.response)


fibonacci_rpc = FibonacciRpcClient()

print(sys.argv)
number = sys.argv[1] if len(sys.argv) > 1 else 30
print(" [x] Requesting fib(%s)".format(number))
response = fibonacci_rpc.call(number)
print(" [.] Got %r" % (response,))
