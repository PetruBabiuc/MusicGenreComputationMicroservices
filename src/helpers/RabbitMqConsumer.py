from __future__ import annotations

import functools
import traceback
from threading import Thread
from typing import Callable
import pika
from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel
from retry import retry
from src.helpers.abstract_classes.AbstractRabbitMqClient import AbstractRabbitMqClient
from src.helpers.abstract_classes.AsyncMessageConsumerInterface import AsyncMessageConsumerInterface


class RabbitMqConsumer(AbstractRabbitMqClient, AsyncMessageConsumerInterface):
    def __init__(self, queue_name: str, message_callback: Callable[[bytes], None]):
        self.__queue_name = queue_name
        self.__received_message_callback = message_callback
        self.__channel: BlockingChannel | None = None
        self.__connection: BlockingConnection | None = None

    def __on_received_message(self, blocking_channel: BlockingChannel, deliver, properties,
                              message):
        try:
            Thread(target=self.__do_work, args=(blocking_channel, deliver.delivery_tag, message)).start()
            # self.__received_message_callback(message)
            # blocking_channel.basic_ack(delivery_tag=deliver.delivery_tag)
        except Exception as e:
            print(f'Exception risen while reading from {self.__queue_name}')
            traceback.print_exc()
            blocking_channel.basic_nack(delivery_tag=deliver.delivery_tag)
        # finally:
        #     blocking_channel.stop_consuming()

    @staticmethod
    def __ack_message(channel: BlockingChannel, delivery_tag):
        if channel.is_open:
            channel.basic_ack(delivery_tag)

    def __do_work(self, channel: BlockingChannel, delivery_tag, message: bytes):
        self.__received_message_callback(message)
        callback = functools.partial(self.__ack_message, channel, delivery_tag)
        self.__connection.add_callback_threadsafe(callback)

    def set_message_callback(self, callback: Callable[[bytes], None]) -> None:
        self.__received_message_callback = callback

    @retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))
    def start_receiving_messages(self) -> None:
        # Automatically close the connection
        with pika.BlockingConnection(self._parameters) as connection:
            self.__connection = connection
            # Automatically close the channel
            with connection.channel() as channel:
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(self.__queue_name,
                                      self.__on_received_message,
                                      # auto_ack=True
                                      )
                try:
                    channel.start_consuming()
                # Don't recover connections closed by server
                except pika.exceptions.ConnectionClosedByBroker:
                    print("[RabbitMqConsumer] Connection closed by broker.")
                    exit(-1)
                # Don't recover on channel errors
                except pika.exceptions.AMQPChannelError:
                    print("[RabbitMqConsumer] AMQP Channel Error")
                    exit(-1)
                # Don't recover from KeyboardInterrupt
                except KeyboardInterrupt:
                    # print("[RabbitMqConsumer] Application closed.")
                    exit(-1)
