import json
from threading import Thread
from typing import Any

from config.rabbit_mq import MP3_VERIFIER_QUEUE
from src.helpers.RabbitMqProducer import RabbitMqProducer
from src.helpers.RedisJsonMessageAwaiter import RedisJsonMessageAwaiter
from src.helpers.abstract_classes.AbstractMessageAwaiter import AbstractMessageAwaiter
from src.helpers.abstract_classes.Mp3ValidatorProxyInterface import Mp3ValidatorProxyInterface


class Mp3ValidatorProxy(Mp3ValidatorProxyInterface):
    def __init__(self, topic: str, key_field: str):
        self.__key_field = key_field
        self.__mp3_validator_sender = RabbitMqProducer(MP3_VERIFIER_QUEUE.exchange, MP3_VERIFIER_QUEUE.routing_key)
        self.__mp3_validation_awaiter: AbstractMessageAwaiter[int, dict[str, Any]] = RedisJsonMessageAwaiter(
            topic, key_field)
        Thread(target=self.__mp3_validation_awaiter.start_receiving_responses).start()

    def validate_song(self, request: dict[str, Any]) -> bool:
        key = request[self.__key_field]
        self.__mp3_validation_awaiter.put_awaitable(key)
        self.__mp3_validator_sender.send_message(json.dumps(request).encode())
        result = self.__mp3_validation_awaiter.await_result(key)
        return result['result']

