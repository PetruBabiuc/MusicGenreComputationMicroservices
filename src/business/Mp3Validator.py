import json
from io import BytesIO
from typing import Callable

from mutagen.mp3 import MP3
from redis.client import StrictRedis

from config import redis
from config.constants import MAX_SONG_LENGTH, MIN_SONG_LENGTH
from config.mp3_validator import SOURCE_TO_TOPIC
from config.rabbit_mq import MP3_VERIFIER_QUEUE
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers import Base64Converter
from src.helpers.RabbitMqConsumer import RabbitMqConsumer


class Mp3Validator(AbstractMicroservice):
    def __init__(self, name: str = 'Mp3Validator', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__message_receiver = RabbitMqConsumer(MP3_VERIFIER_QUEUE.name, self.__on_received_message)
        self.__redis = StrictRedis(redis.HOST, redis.PORT, encoding='utf-8', decode_responses=True)
        self._log_func(f'[{self._name}] Microservice started!')

    def __on_received_message(self, message: bytes) -> None:
        message = json.loads(message)
        source = message['source']
        del message['source']

        song = message['song']
        song = Base64Converter.string_to_bytes(song)
        del message['song']

        message['result'] = self.__validate_song(song)
        # The song identifier is left untouched.
        self.__redis.publish(SOURCE_TO_TOPIC[source], json.dumps(message))

    @staticmethod
    def __validate_song(song: bytes) -> bool:
        try:
            song = BytesIO(song)
            song = MP3(song)
            return MIN_SONG_LENGTH <= song.info.length <= MAX_SONG_LENGTH
        except BaseException:
            return False

    def run(self) -> None:
        self.__message_receiver.start_receiving_messages()


if __name__ == '__main__':
    Mp3Validator().run()
