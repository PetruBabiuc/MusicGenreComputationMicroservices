import os.path
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable, Any

from config import constants, controller, genre_computer_request_manager
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.SocketJsonMessageAwaiter import SocketJsonMessageAwaiter
from src.helpers.SynchronizedDict import SynchronizedDict
from src.model.AwaitableResult import AwaitableResult
from src.persistence.DatabaseManagerStub import DatabaseManagerStub


class Controller(AbstractMicroservice):
    def __init__(self, name: str = 'Controller', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)

        self.__client_server_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__client_server_socket.bind((controller.HOST, controller.CLIENT_PORT))
        self.__client_server_socket.listen()
        self._log_func(f'[{self._name}] ServerSocket for clients '
                       f'opened on {controller.HOST}:{controller.CLIENT_PORT}!')

        self.__results_awaiter: SocketJsonMessageAwaiter[int] = SocketJsonMessageAwaiter(
            controller.HOST, controller.GENRE_COMPUTATION_PORT, 'song_id')

        self._log_func(f'[{self._name}] ServerSocket for computation results '
                       f'opened on {controller.HOST}:{controller.GENRE_COMPUTATION_PORT}!')

        self.__db_manager = DatabaseManagerStub()
        self.__song_id_to_awaitable_result_package: SynchronizedDict[int, AwaitableResult[dict[str, Any]]] = \
            SynchronizedDict()

        # Temporary :(
        self.__song_id_to_awaitable_result_package['id'] = 0

    def __serve_client(self, client_socket: HighLevelSocketWrapper, addr) -> None:
        message = client_socket.receive_json_as_dict()
        song_name = message['song_name']

        # TODO: Get genre from DB
        # with self.__db_manager as db_manager:
        #     genre = db_manager.get_song_genre(song_name)

        genre = None

        self._log_func(f'[{self._name}] Genre of the song {song_name} requested by {addr}: {genre}')
        message = {'genre': genre}
        client_socket.send_dict_as_json(message)

        # Song's genre already computed
        if genre is not None:
            self._log_func(f"[{self._name}] {addr}'s song's genre already computed => Done!")
            client_socket.close()
            return

        # Song's genre will be computed
        self._log_func(f"[{self._name}] Waiting {addr}'s song bytes...")
        message = client_socket.receive_message()
        self._log_func(f"[{self._name}] {addr}'s song bytes: {len(message)}")

        # TODO: Insert new database entry
        # Creating new database entry
        # with self.__db_manager as db_manager:
        #     song_id = db_manager.insert_song_data_row(song_name)

        # Temporary :(
        with self.__song_id_to_awaitable_result_package as sync_dict:
            song_id = sync_dict['id']
            sync_dict['id'] += 1
        # song_id = random.randint(0, 10_000)

        self.__results_awaiter.put_awaitable(song_id)

        # Sending song for genre computation
        self._compute_song_genre(song_id, message)

        # Awaiting genre computation
        message = self.__results_awaiter.await_result(song_id)

        # TODO: To remove, this is GenreComputerRequestManager's functionality
        # with self.__db_manager as db_manager:
        #     db_manager.update_song_genre(song_id, message['genre'])

        client_socket.send_dict_as_json(message)
        client_socket.close()

    def _compute_song_genre(self, song_id: int, song_bytes: bytes) -> None:
        message = song_id.to_bytes(constants.ID_FIELD_SIZE, 'big')
        message += song_bytes
        client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        client_socket.connect((genre_computer_request_manager.HOST, genre_computer_request_manager.REQUESTS_PORT))
        client_socket.send_dict_as_json({
            'source': 'Controller',
            'song_id': song_id
        })
        client_socket.send_message(song_bytes)
        client_socket.close()

    def __serve_client_task(self):
        while True:
            client_socket, addr = self.__client_server_socket.accept()
            self._log_func(f'[{self._name}] Client connected: {addr}')
            Thread(target=self.__serve_client, args=(client_socket, addr)).start()

    def run(self) -> None:
        try:
            Thread(target=self.__serve_client_task).start()
            self.__results_awaiter.start_receiving_responses()
        finally:
            self.__client_server_socket.close()


class DebugController(Controller):
    def __init__(self, output_dir: str = '.', name: str = 'Controller', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__output_dir = output_dir

    def _compute_song_genre(self, request_id: int, song_bytes: bytes) -> None:
        with open(os.path.join(self.__output_dir, 'Controller - Song.mp3'), 'wb') as f:
            f.write(song_bytes)
        super()._compute_song_genre(request_id, song_bytes)


if __name__ == '__main__':
    # Controller().run()
    DebugController('../../debug_files/').run()
