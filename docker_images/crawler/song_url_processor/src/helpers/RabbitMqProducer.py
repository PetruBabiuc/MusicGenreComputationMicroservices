import pika
from src.helpers.abstract_classes.AbstractRabbitMqClient import AbstractRabbitMqClient
from src.helpers.abstract_classes.MessageProducerInterface import MessageProducerInterface


class RabbitMqProducer(AbstractRabbitMqClient, MessageProducerInterface):
    def __init__(self, exchange: str, routing_key: str):
        self.__exchange = exchange
        self.__routing_key = routing_key

    def send_message(self, message: bytes):
        # Automatically close the connection
        with pika.BlockingConnection(self._parameters) as connection:
            # Automatically close the channel
            with connection.channel() as channel:
                channel.basic_publish(exchange=self.__exchange,
                                      routing_key=self.__routing_key,
                                      body=message)
