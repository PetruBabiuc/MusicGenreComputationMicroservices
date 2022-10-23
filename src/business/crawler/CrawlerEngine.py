from __future__ import annotations

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable, Any

from config.crawler_engine import HOST as CRAWLER_HOST, PORT as CRAWLER_PORT
from config.crawler_state_repository import HOST as STATE_REPOSITORY_HOST, PORT as STATE_REPOSITORY_PORT
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper


class CrawlerEngine(AbstractMicroservice):
    def __init__(self, name: str = 'CrawlerEngine', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)

        self.__server_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__server_socket.bind((CRAWLER_HOST, CRAWLER_PORT))
        self.__server_socket.listen()
        self._log_func(f'[{self._name}] ServerSocket opened for Controller on {CRAWLER_HOST}:{CRAWLER_PORT}')

    def __receive_controller_requests(self) -> None:
        while True:
            con, _ = self.__server_socket.accept()
            Thread(target=self.__handle_controller_request, args=(con,)).start()

    def __handle_controller_request(self, client_socket: HighLevelSocketWrapper) -> None:
        message = client_socket.receive_json_as_dict()

        result = None
        client_id = message['client_id']

        if message['operation'] == 'get_song':
            self.__get_song(client_id, message['genre'])

        self._log_func(f'[{self._name}] Controller request:'
                       f'\n\tRequest: {message}'
                       f'\n\tResult: {result}')

        client_socket.close()

    @staticmethod
    def __call_repository(operation: str, client_id: int,
                          has_return: bool, params: dict[str, Any] = None) -> dict[str, Any] | None:
        message = dict(params) if params else {}
        message['operation'] = operation
        message['client_id'] = client_id

        client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        client_socket.connect((STATE_REPOSITORY_HOST, STATE_REPOSITORY_PORT))
        client_socket.send_dict_as_json(message)

        result = client_socket.receive_json_as_dict() if has_return else None
        client_socket.close()
        return result

    def __get_song(self, client_id: int, genre: str) -> None:
        message = {
            'client_id': client_id,
        }

        # TODO...
