#!/usr/bin/env python
# coding: utf-8
import pika
import sys
"""
上一篇教程里，我们改进了我们的日志系统。我们使用直连交换机替代了扇型交换机，从只能盲目的广播消息改进为有可能选择性的接收日志。
尽管直连交换机能够改善我们的系统，但是它也有它的限制 —— 没办法基于多个标准执行路由操作。
在我们的日志系统中，我们不只希望订阅基于严重程度的日志，同时还希望订阅基于发送来源的日志。
Unix工具syslog就是同时基于严重程度-severity (info/warn/crit...) 和 设备-facility (auth/cron/kern...)来路由日志的。
如果这样的话，将会给予我们非常大的灵活性，我们既可以监听来源于“cron”的严重程度为“critical errors”的日志，
也可以监听来源于“kern”的所有日志。
为了实现这个目的，接下来我们学习如何使用另一种更复杂的交换机 —— 主题交换机。

主题交换机
发送到主题交换机（topic exchange）的消息不可以携带随意什么样子的路由键（routing_key），它的路由键必须是一个由.
分隔开的词语列表。这些单词随便是什么都可以，但是最好是跟携带它们的消息有关系的词汇。
以下是几个推荐的例子："stock.usd.nyse", "nyse.vmw", "quick.orange.rabbit"。词语的个数可以随意，但是不要超过255字节。
绑定键也必须拥有同样的格式。主题交换机背后的逻辑跟直连交换机很相似 —— 一个携带着特定路由键的消息会被主题交换机投递给
绑定键与之想匹配的队列。但是它的绑定键和路由键有两个特殊应用方式：
    * (星号) 用来表示一个单词.
    # (井号) 用来表示任意数量（零个或多个）单词。
这个例子里，我们发送的所有消息都是用来描述小动物的。发送的消息所携带的路由键是由三个单词所组成的，这三个单词被两个.分割开。
路由键里的第一个单词描述的是动物的手脚的利索程度，第二个单词是动物的颜色，第三个是动物的种类。
所以它看起来是这样的： <celerity>.<colour>.<species>。

我们创建了三个绑定：Q1的绑定键为 `*.orange.*`，Q2的绑定键为 `*.*.rabbit` 和 `lazy.#` 。
这三个绑定键被可以总结为：
    Q1 对所有的桔黄色动物都感兴趣。
    Q2 则是对所有的兔子和所有懒惰的动物感兴趣。
一个携带有 `quick.orange.rabbit` 的消息将会被分别投递给这两个队列。
携带着 `lazy.orange.elephant` 的消息同样也会给两个队列都投递过去。
另一方面携带有 quick.orange.fox 的消息会投递给第一个队列，携带有 lazy.brown.fox 的消息会投递给第二个队列。
携带有 lazy.pink.rabbit 的消息只会被投递给第二个队列一次，即使它同时匹配第二个队列的两个绑定。
携带着 quick.brown.fox 的消息不会投递给任何一个队列。

如果我们违反约定，发送了一个携带有一个单词或者四个单词（"orange" or "quick.orange.male.rabbit"）的消息时，
发送的消息不会投递给任何一个队列，而且会丢失掉。
但是另一方面，即使 "lazy.orange.male.rabbit" 有四个单词，他还是会匹配最后一个绑定，并且被投递到第二个队列中。
"""
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs',
                         exchange_type='topic')

routing_key = sys.argv[1] if len(sys.argv) > 1 else 'anonymous.info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(exchange='topic_logs',
                      routing_key=routing_key,
                      body=message)
print(" [x] Sent %r:%r" % (routing_key, message))
connection.close()
