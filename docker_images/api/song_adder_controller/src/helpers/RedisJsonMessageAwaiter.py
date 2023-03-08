import json
from typing import TypeVar, Any

from redis.client import StrictRedis

from config.redis import HOST, PORT
from src.helpers.abstract_classes.AbstractMessageAwaiter import AbstractMessageAwaiter

K = TypeVar('K')


class RedisJsonMessageAwaiter(AbstractMessageAwaiter[K, dict[str, Any]]):
    def __init__(self, topic: str, key_field: str):
        super().__init__()
        red = StrictRedis(HOST, PORT, encoding='utf-8', decode_responses=True)
        self.__topic = topic
        self.__sub = red.pubsub(ignore_subscribe_messages=True)
        self.__sub.subscribe(topic)
        self.__key_field = key_field

    def put_awaitable(self, key: K) -> None:
        if self.awaited_messages_count() == 0 and not self.__sub.subscribed:
            self.__sub.subscribe(self.__topic)
        super().put_awaitable(key)

    def start_receiving_responses(self) -> None:
        try:
            for message in self.__sub.listen():
                message = json.loads(message['data'])
                key = message[self.__key_field]
                if not self.contains_key(key):
                    continue  # The message may be for another consumer of the topic
                del message[self.__key_field]
                self._put_result_and_notify(key, message)
                if self.awaited_messages_count() == 0 and self.__sub.subscribed:
                    self.__sub.reset()

        finally:
            self.__sub.close()
