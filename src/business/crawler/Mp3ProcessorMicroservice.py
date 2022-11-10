import json
import time
from socket import socket, AF_INET, SOCK_STREAM
from typing import Callable, Any
from urllib.parse import urljoin

import requests

from config import crawler_genre_obtainer
from config.constants import ID_FIELD_SIZE
from config.rabbit_mq import Crawler
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers import Base64Converter
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.RabbitMqConsumer import RabbitMqConsumer
from src.helpers.RabbitMqProducer import RabbitMqProducer


class Mp3ProcessorMicroservice(AbstractMicroservice):
    def __init__(self, name: str = 'Mp3Processor', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__sender = RabbitMqProducer(Crawler.UrlProcessors.RETURN_QUEUE.exchange,
                                         Crawler.UrlProcessors.RETURN_QUEUE.routing_key)
        self.__consumer = RabbitMqConsumer(Crawler.UrlProcessors.RESTORE_STATE_QUEUE.name,
                                           self.__on_receive_message)
        self._log_func(f'[{self._name}] Microservice started!')

    def __on_receive_message(self, message: bytes) -> None:
        message = json.loads(message.decode())
        domain = message['domain']
        client_id = message['client_id']
        desired_genre = message['genre']
        urls = message['urls']

        self._log_func(f'[{self._name}] Received request:'
                       f'\n\tClientID: {client_id}'
                       f'\n\tDesired genre: {desired_genre}'
                       f'\n\tDomain: {domain}'
                       f'\n\tURLs: {urls}')

        response = {'client_id': client_id}
        genre_to_urls = {}

        for index, url in enumerate(urls):
            absolute_url = urljoin(domain, url)
            self.__schedule_request(domain)
            song = requests.get(absolute_url, timeout=10)  # seconds
            if not song.ok:
                self._log_func(f'[{self._name}] Timeout on GET request for {absolute_url}')
                continue
            song = song.content

            # TODO: Revert DEBUG CODE
            # with open('/home/petru/Licenta/Microservices/tests/presentation/found_song.mp3', 'rb') as f:
            #     song = f.read()

            genre = self.__compute_genre(client_id, song)['genre']

            # SongGenreObtainer stopped computing genres, so we should stop requesting genre computations
            if genre == 'Computing...':
                response['unchecked_urls'] = urls[index:]
                break

            if genre in desired_genre:
                response['song'] = Base64Converter.bytes_to_string(song)
                response['song_url'] = url
                if index < len(urls) - 1:
                    response['unchecked_urls'] = urls[index + 1:]
                break

            if genre not in genre_to_urls:
                genre_to_urls[genre] = []
            genre_to_urls[genre].append(url)

        if genre_to_urls:
            response['genre_to_urls'] = genre_to_urls

        response_to_print = dict(response)
        if 'song' in response_to_print:
            response_to_print['song'] = f'{len(response["song"])} Base64 characters...'
        self._log_func(f'[{self._name}] Response: {response_to_print}')
        self.__return_response(response)

    def __return_response(self, response: dict[str, Any]) -> None:
        response = json.dumps(response).encode()
        self.__sender.send_message(response)

    @staticmethod
    def __compute_genre(client_id: int, song: bytes) -> dict[str, Any]:
        message = client_id.to_bytes(ID_FIELD_SIZE, 'big', signed=False) + song
        client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        client_socket.connect((crawler_genre_obtainer.HOST, crawler_genre_obtainer.URL_PROCESSOR_PORT))
        client_socket.send_message(message)
        response = client_socket.receive_json_as_dict()
        client_socket.close()
        return response

    @staticmethod
    def __schedule_request(domain: str):
        time.sleep(0.75)

    def run(self) -> None:
        self.__consumer.start_receiving_messages()


if __name__ == '__main__':
    Mp3ProcessorMicroservice().run()
