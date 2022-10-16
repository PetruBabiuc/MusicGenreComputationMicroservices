from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from typing import Callable

from config.primary_database import HOST, PORT
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper


class PrimaryDatabaseMicroservice(AbstractMicroservice):
    def __init__(self, name: str = 'PrimaryDatabaseMicroservice', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__server_socker = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__server_socker.bind((HOST, PORT))
        self.__server_socker.listen()
        self._log_func(f'[{self._name}] ServerSocket started on {HOST}:{PORT}')

    def __handle_request(self, con: HighLevelSocketWrapper, addr: tuple[str, int]) -> None:
        request = con.receive_json_as_dict()
        self._log_func(f'[{self._name}] Request received:'
                       f'\n\tClient: {addr}'
                       f'\n\tRequest: {request}')

        operation = request['operation']
        if operation == 'get_song_genre':
            pass

        con.close()

    def run(self):
        while True:
            con, addr = self.__server_socker.accept()
            Thread(target=self.__handle_request, args=(con, addr)).start()


if __name__ == '__main__':
    PrimaryDatabaseMicroservice().run()
