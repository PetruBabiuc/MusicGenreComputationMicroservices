from abc import ABCMeta
from config import rabbit_mq
import pika


class AbstractRabbitMqClient(metaclass=ABCMeta):
    _credentials = pika.PlainCredentials(rabbit_mq.USERNAME, rabbit_mq.PASSWORD)
    _parameters = (pika.ConnectionParameters(host=rabbit_mq.HOST),
                   pika.ConnectionParameters(port=rabbit_mq.PORT),
                   pika.ConnectionParameters(credentials=_credentials),
                   )
