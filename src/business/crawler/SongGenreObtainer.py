from __future__ import annotations

import random
from io import BytesIO
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable

import requests
from mutagen.id3 import ID3

from config.constants import ID_FIELD_SIZE
from config.crawler_genre_obtainer import HOST, COMPUTATION_RESULTS_PORT, URL_PROCESSOR_PORT
from config.database_api import *
from config.database_api_credentials import MICROSERVICE_CREDENTIALS
from config.dnn import GENRES
from config.genre_computer_request_manager import HOST as REQUEST_MANAGER_HOST, REQUESTS_PORT as REQUEST_MANAGER_PORT
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers.DatabaseApiProxy import DatabaseApiProxy
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.SocketJsonMessageAwaiter import SocketJsonMessageAwaiter


class SongGenreObtainer(AbstractMicroservice):
    def __init__(self, name: str = 'SongGenreObtainer', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__genre_awaiter: SocketJsonMessageAwaiter[int] = SocketJsonMessageAwaiter(
            HOST, COMPUTATION_RESULTS_PORT, 'client_id')
        self._log_func(f'[{self._name}] ServerSocket for genre computation results opened on '
                       f'{HOST}:{COMPUTATION_RESULTS_PORT}')

        self.__url_processor_server_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__url_processor_server_socket.bind((HOST, URL_PROCESSOR_PORT))
        self.__url_processor_server_socket.listen()

        self.__database_proxy = DatabaseApiProxy(*MICROSERVICE_CREDENTIALS)

        # TODO: REMOVE OLD CODE
        self.__genre_computation_service_id = self.__database_proxy.get_services(
            service_name='genre_computation'
        )[0]['service_id']
        # self.__genre_computation_service_id = requests.get(API_URL_PREFIX + SERVICES_PATH, params={
        #     'service_name': 'genre_computation'
        # }).json()[0]['service_id']

        self._log_func(f'[{self._name}] ServerSocket for URL Processors opened on {HOST}:{URL_PROCESSOR_PORT}')

    @staticmethod
    def __get_genre_from_metadata(song: bytes) -> str | None:
        song = BytesIO(song)
        try:
            id3 = ID3(song)
        except BaseException:  # ID#NoHeaderException etc
            return

        genre = id3.get('TCON', default=None)
        if not genre:
            return
        genre = genre.text[0]

        for g in GENRES:
            if g.casefold() == genre.casefold():
                return g

    def __handle_request(self, url_processor_socket: HighLevelSocketWrapper) -> None:
        # ID + Song
        message = url_processor_socket.receive_message()
        song = message[ID_FIELD_SIZE:]

        client_id = message[:ID_FIELD_SIZE]
        client_id = int.from_bytes(client_id, 'big', signed=False)

        # Trying to get the genre from song's ID3 metadata
        if genre := self.__get_genre_from_metadata(song):
            url_processor_socket.send_dict_as_json({'genre': genre})
            url_processor_socket.close()
            self._log_func(f'[{self._name}] Request handled:'
                           f'\n\tSong bytes: {len(message)}'
                           f'\n\tClient ID: {client_id}'
                           f'\n\tGenre: {genre}'
                           f'\n\tGenre obtained from embedded metadata (ID3)!')
            return

        message = {'source': 'Crawler', 'client_id': client_id}

        # TODO: REMOVE OLD CODE
        max_computed_genres = self.__database_proxy.get_crawler_state(client_id)['max_computed_genres']
        # max_computed_genres = requests.get(API_URL_PREFIX + CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # })).json()['max_computed_genres']
        if max_computed_genres == 0:
            result = {'genre': 'Computing...'}
        else:
            request_manager_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
            request_manager_socket.connect((REQUEST_MANAGER_HOST, REQUEST_MANAGER_PORT))

            self.__genre_awaiter.put_awaitable(client_id)

            # Complete message for RequestManager: dict -> JSON string -> UTF-8 encoded string + song bytes
            request_manager_socket.send_dict_as_json(message)
            request_manager_socket.send_message(song)
            request_manager_socket.close()

            result = self.__genre_awaiter.await_result(client_id)

            # TODO: REMOVE DEBUG CODE
            # result = {'genre': random.choice(GENRES)}

            self.__database_proxy.patch_crawler_state(client_id, {'max_computed_genres': max_computed_genres - 1})

            # TODO: REMOVE OLD CODE
            # quantity = requests.get(API_URL_PREFIX + USERS_TO_SERVICES_PATH, params={
            #     'user_id': client_id,
            #     'service_id': self.__genre_computation_service_id
            # }).json()[0]['quantity']
            # requests.patch(API_URL_PREFIX + USERS_TO_SERVICES_PATH, params={
            #     'user_id': client_id,
            #     'service_id': self.__genre_computation_service_id
            # }, json={
            #     'quantity': quantity + 1
            # })

        self._log_func(f'[{self._name}] Request handled:'
                       f'\n\tClient ID: {client_id}'
                       f'\n\tResult: {result}'
                       f'\n\tGenre computed using the pipeline!')
        url_processor_socket.send_dict_as_json(result)
        url_processor_socket.close()

    def __receive_requests(self):
        while True:
            con, _ = self.__url_processor_server_socket.accept()
            Thread(target=self.__handle_request, args=(con,)).start()

    def run(self) -> None:
        try:
            Thread(target=self.__receive_requests).start()
            self.__genre_awaiter.start_receiving_responses()
        finally:
            self.__url_processor_server_socket.close()


if __name__ == '__main__':
    SongGenreObtainer().run()
