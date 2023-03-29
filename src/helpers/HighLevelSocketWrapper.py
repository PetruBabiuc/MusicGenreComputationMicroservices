from __future__ import annotations
import json
import os.path
from socket import socket, error as socket_error, SOL_SOCKET, SO_REUSEADDR
from typing import Any

from src.helpers.abstract_classes.MessageProducerInterface import MessageProducerInterface
from src.helpers.abstract_classes.SyncMessageConsumerInterface import SyncMessageConsumerInterface


class HighLevelSocketWrapper(SyncMessageConsumerInterface, MessageProducerInterface):
    def __init__(self, _socket: socket):
        _socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.__header_bytes_number = 4

        self.bind = _socket.bind
        self.connect = _socket.connect
        self.listen = _socket.listen
        self.close = _socket.close

        self.__accept = _socket.accept
        self.__sendfile = _socket.sendfile
        self.__sendall = _socket.sendall
        self.__recv = _socket.recv

    def accept(self) -> tuple[HighLevelSocketWrapper, tuple[str, int]]:
        _socket, addr = self.__accept()
        _socket = HighLevelSocketWrapper(_socket)
        return _socket, addr

    def set_payload_size_bytes_number_header(self, bytes_number: int) -> None:
        assert bytes_number > 0
        self.__header_bytes_number = bytes_number

    def send_message(self, message: bytes) -> None:
        header = len(message).to_bytes(self.__header_bytes_number, 'big', signed=False)
        self.__sendall(header)
        self.__sendall(message)

    def receive_message(self) -> bytes:
        received_bytes = bytearray()
        bytes_to_receive = self.__recv(self.__header_bytes_number)
        bytes_to_receive = int.from_bytes(bytes_to_receive, 'big', signed=False)
        while len(received_bytes) < bytes_to_receive:
            block = self.__recv(bytes_to_receive - len(received_bytes))
            if not block:
                raise socket_error(f'Stopped receiving data! '
                                   f'Received {len(received_bytes)} out of {bytes_to_receive}')
            received_bytes.extend(block)
        return bytes(received_bytes)

    def send_dict_as_json(self, _dict: dict[str, Any]) -> None:
        message = json.dumps(_dict)
        message = message.encode()
        self.send_message(message)

    def receive_json_as_dict(self) -> dict[str, Any]:
        message = self.receive_message()
        message = message.decode()
        message = json.loads(message)
        return message

    def sendfile(self, file_path: str) -> None:
        bytes_number = os.path.getsize(file_path).to_bytes(self.__header_bytes_number, 'big', signed=False)
        self.__sendall(bytes_number)
        with open(file_path, 'rb') as f:
            self.__sendfile(f)
