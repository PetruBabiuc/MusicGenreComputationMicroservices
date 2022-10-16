from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import TypeVar, Any

from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.abstract_classes.AbstractMessageAwaiter import AbstractMessageAwaiter

K = TypeVar('K')


class SocketJsonMessageAwaiter(AbstractMessageAwaiter[K, dict[str, Any]]):
    def __init__(self, host: str, port: int, key_field: str):
        super().__init__()
        self.__server_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__server_socket.bind((host, port))
        self.__server_socket.listen()

        self.__key_field = key_field

    def __receive_response(self, con: HighLevelSocketWrapper) -> None:
        message = con.receive_json_as_dict()
        key = message[self.__key_field]
        del message[self.__key_field]
        self._put_result_and_notify(key, message)

    def start_receiving_responses(self) -> None:
        try:
            while True:
                con, _ = self.__server_socket.accept()
                Thread(target=self.__receive_response, args=(con,)).start()
        finally:
            self.__server_socket.close()
