import os.path
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Event
from typing import Callable
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.RabbitMqProducer import RabbitMqProducer
from src.helpers.SynchronizedDict import SynchronizedDict
from src.model.AwaitableResult import AwaitableResult
from src.persistence.DatabaseManagerStub import DatabaseManagerStub
from config import rabbit_mq, constants, controller


class Controller(AbstractMicroservice):
    def __init__(self, name: str = 'Controller', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__message_sender = RabbitMqProducer(rabbit_mq.SONGS_QUEUE.exchange,
                                                 rabbit_mq.SONGS_QUEUE.routing_key)

        self.__client_server_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__client_server_socket.bind((controller.HOST, controller.CLIENT_PORT))
        self.__client_server_socket.listen()
        self._log_func(f'[{self._name}] ServerSocket for clients opened on {controller.HOST}:{controller.CLIENT_PORT}!')

        self.__results_server_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__results_server_socket.bind((controller.HOST, controller.RESULTS_PORT))
        self.__results_server_socket.listen()
        self._log_func(f'[{self._name}] ServerSocket for computation results '
                       f'opened on {controller.HOST}:{controller.RESULTS_PORT}!')

        self.__db_manager = DatabaseManagerStub()
        self.__song_id_to_awaitable_result_package: SynchronizedDict[int, AwaitableResult] = SynchronizedDict()

    def __serve_client(self, client_socket: HighLevelSocketWrapper, addr) -> None:
        message = client_socket.receive_json_as_dict()
        song_name = message['song_name']
        with self.__db_manager as db_manager:
            genre = db_manager.get_song_genre(song_name)

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

        # Creating new database entry
        with self.__db_manager as db_manager:
            song_id = db_manager.insert_song_data_row(song_name)

        # Creating new entry in the synchronized dict:
        # song_id -> (event, None)
        event = Event()
        with self.__song_id_to_awaitable_result_package as sync_dict:
            sync_dict[song_id] = AwaitableResult(event)

        # Sending song for genre computation
        self._convert_song_into_spectrogram(song_id, message)

        # Awaiting genre computation
        event.wait()
        with self.__song_id_to_awaitable_result_package as sync_dict:
            message = sync_dict[song_id].result
            del sync_dict[song_id]

        with self.__db_manager as db_manager:
            db_manager.update_song_genre(song_id, message['genre'])

        client_socket.send_dict_as_json(message)
        client_socket.close()

    def _convert_song_into_spectrogram(self, song_id: int, song_bytes: bytes) -> None:
        message = song_id.to_bytes(constants.ID_FIELD_SIZE, 'big')
        message += song_bytes
        self.__message_sender.send_message(message)

    def __receive_computation_results(self, client_socket: HighLevelSocketWrapper, addr: tuple[str, int]) -> None:
        result = client_socket.receive_json_as_dict()

        self._log_func(f'[{self._name}] Genre computation received:'
                       f'\n\tSender: {addr}'
                       f'\n\tContent: {result}')

        song_id = result['song_id']
        del result['song_id']

        with self.__song_id_to_awaitable_result_package as sync_dict:
            result_package = sync_dict[song_id]
            result_package.result = result
            result_package.event.set()

        client_socket.close()

    def __serve_client_task(self):
        while True:
            client_socket, addr = self.__client_server_socket.accept()
            self._log_func(f'[{self._name}] Client connected: {addr}')
            Thread(target=self.__serve_client, args=(client_socket, addr)).start()

    def __receive_computation_results_task(self):
        while True:
            client_socket, addr = self.__results_server_socket.accept()
            Thread(target=self.__receive_computation_results, args=(client_socket, addr)).start()

    def run(self) -> None:
        try:
            Thread(target=self.__serve_client_task).start()
            self.__receive_computation_results_task()
        finally:
            self.__client_server_socket.close()
            self.__results_server_socket.close()


class DebugController(Controller):
    def __init__(self, output_dir: str = '.', name: str = 'Controller', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__output_dir = output_dir

    def _convert_song_into_spectrogram(self, song_id: int, song_bytes: bytes) -> None:
        with open(os.path.join(self.__output_dir, 'Controller - Song.mp3'), 'wb') as f:
            f.write(song_bytes)
        super()._convert_song_into_spectrogram(song_id, song_bytes)


if __name__ == '__main__':
    # Controller().run()
    DebugController('../../debug_files/').run()
