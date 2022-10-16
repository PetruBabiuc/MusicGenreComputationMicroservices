from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable, Any
from uuid import uuid4

import config.crawler_genre_obtainer as crawler
from config import controller, primary_database
from config.genre_computer_request_manager import HOST, REQUESTS_PORT, RESULTS_PORT
from config.rabbit_mq import GenreComputationPipeline
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers import Base64Converter
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.RabbitMqProducer import RabbitMqProducer
from src.helpers.SynchronizedDict import SynchronizedDict


class GenreComputerRequestManager(AbstractMicroservice):
    def __init__(self, name: str = 'GenreComputerRequestManager', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)

        self.__requests_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__requests_socket.bind((HOST, REQUESTS_PORT))
        self.__requests_socket.listen()
        self._log_func(f'[{self._name}] ServerSocket for requests opened on {HOST}:{REQUESTS_PORT}...')

        self.__results_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__results_socket.bind((HOST, RESULTS_PORT))
        self.__results_socket.listen()
        self._log_func(f'[{self._name}] ServerSocket for requests opened on {HOST}:{RESULTS_PORT}...')

        self.__song_sender = RabbitMqProducer(GenreComputationPipeline.SONGS_QUEUE.exchange,
                                              GenreComputationPipeline.SONGS_QUEUE.routing_key)
        self.__request_id_to_request_info = SynchronizedDict()

    def __forward_request(self, con: HighLevelSocketWrapper, addr: tuple[str, int]) -> None:
        request = con.receive_json_as_dict()
        song = con.receive_message()
        con.close()

        request_id = uuid4().hex

        with self.__request_id_to_request_info as sync_dict:
            sync_dict[request_id] = request

        request_id_bytes = Base64Converter.string_to_bytes(request_id)
        self.__song_sender.send_message(request_id_bytes + song)
        self._log_func(f'[{self._name}] Received request:'
                       f'\n\tClient: {addr}'
                       f'\n\tInfo: {request}'
                       f'\n\tSong bytes: {len(song)}'
                       f'\n\tRequestID: {request_id}')

    def __receive_responses(self) -> None:
        while True:
            con, addr = self.__results_socket.accept()
            Thread(target=self.__route_response, args=(con, addr)).start()

    def __receive_requests(self) -> None:
        while True:
            con, addr = self.__requests_socket.accept()
            Thread(target=self.__forward_request, args=(con, addr)).start()

    @staticmethod
    def __route_response_to_db(result: dict[str, Any]) -> None:
        return
        # result['operation'] = 'update_song_genre'
        # con = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        # con.connect((primary_database.HOST, primary_database.PORT))
        # con.send_dict_as_json(result)
        # con.close()

    def __route_response(self, con: HighLevelSocketWrapper, addr: tuple[str, int]) -> None:
        message = con.receive_json_as_dict()
        con.close()

        request_id = message['request_id']

        with self.__request_id_to_request_info as sync_dict:
            request_info = sync_dict[request_id]
            del sync_dict[request_id]

        self._log_func(f'[{self._name}] Received genre computation result:'
                       f'\n\tClient: {addr}'
                       f'\n\tResult: {message}'
                       f'\n\tParent request: {request_info}')

        source = request_info['source']
        del request_info['source']
        result = request_info
        result['genre'] = message['genre']

        if source == 'Controller':
            self.__route_response_to_db(result)
            self.__route_dict_response_as_json(controller.HOST, controller.GENRE_COMPUTATION_PORT, result)

        elif source == 'Crawler':
            self.__route_dict_response_as_json(crawler.HOST, crawler.COMPUTATION_RESULTS_PORT, result)

    def run(self) -> None:
        try:
            Thread(target=self.__receive_requests).start()
            self.__receive_responses()
        finally:
            self.__requests_socket.close()
            self.__results_socket.close()

    @staticmethod
    def __route_dict_response_as_json(host: str, port: int, result: dict[str, Any]):
        con = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        con.connect((host, port))
        con.send_dict_as_json(result)
        con.close()


if __name__ == '__main__':
    GenreComputerRequestManager().run()
