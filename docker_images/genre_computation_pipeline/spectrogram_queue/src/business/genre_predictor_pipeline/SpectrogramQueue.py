import os.path
from queue import Queue
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable
from config import spectrogram_queue
from config.constants import SLICES_NUMBER_BYTES
from config.genre_computer_request_manager import REQUEST_ID_BYTES_NUMBER
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper


class SpectrogramQueue(AbstractMicroservice):
    def __init__(self, name: str = 'SpectrogramQueue', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__put_server_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__put_server_socket.bind((spectrogram_queue.HOST, spectrogram_queue.PUT_PORT))
        self.__put_server_socket.listen()
        self._log_func(f'[{self._name}] ServerSocket for PUT '
                       f'opened on {spectrogram_queue.HOST}:{spectrogram_queue.PUT_PORT}')

        self.__get_server_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__get_server_socket.bind((spectrogram_queue.HOST, spectrogram_queue.GET_PORT))
        self.__get_server_socket.listen()
        self._log_func(f'[{self._name}] ServerSocket for GET '
                       f'opened on {spectrogram_queue.HOST}:{spectrogram_queue.GET_PORT}')

        self.__queue: Queue[tuple[bytes, bytes, bytes]] = Queue()

    def __handle_get_clients(self) -> None:
        try:
            while True:
                request_id, slice_index, spectrogram = self.__queue.get()
                client_socket, addr = self.__get_server_socket.accept()
                message = request_id + slice_index + spectrogram

                slice_index = int.from_bytes(slice_index, 'big', signed=False)

                self._log_func(f'[{self._name}] GET:'
                               f'\n\tClient: {addr}'
                               f'\n\tRequestID: {request_id}'
                               f'\n\tSliceIndex: {slice_index}'
                               f'\n\tSpectrogram bytes: {len(spectrogram)}')
                Thread(target=client_socket.send_message, args=(message,)).start()
        finally:
            self.__get_server_socket.close()

    def __handle_put_clients(self) -> None:
        try:
            while True:
                client_socket, addr = self.__put_server_socket.accept()
                Thread(target=self.__put_task, args=(client_socket, addr)).start()
        finally:
            self.__get_server_socket.close()

    def _put_message(self, message: bytes, addr: tuple[str, int]) -> None:
        slices_number = message[REQUEST_ID_BYTES_NUMBER:REQUEST_ID_BYTES_NUMBER + SLICES_NUMBER_BYTES]
        slices_number = int.from_bytes(slices_number, 'big', signed=False)
        request_id = message[:REQUEST_ID_BYTES_NUMBER]
        spectrogram = message[REQUEST_ID_BYTES_NUMBER + SLICES_NUMBER_BYTES:]
        for slice_index in range(slices_number):
            slice_index = slice_index.to_bytes(SLICES_NUMBER_BYTES, 'big', signed=False)
            self.__queue.put((request_id, slice_index, spectrogram))
        self._log_func(f'[{self._name}] PUT:'
                       f'\n\tClient: {addr}'
                       f'\n\tRequestID: {request_id}'
                       f'\n\tSlices number: {slices_number}'
                       f'\n\tSpectrogram bytes: {len(spectrogram)}')

    def __put_task(self, client_socket: HighLevelSocketWrapper, addr: tuple[str, int]) -> None:
        message = client_socket.receive_message()
        self._put_message(message, addr)

    def run(self) -> None:
        try:
            Thread(target=self.__handle_put_clients).start()
            self.__handle_get_clients()
        finally:
            exit(0)


class DebugSpectrogramQueue(SpectrogramQueue):
    def __init__(self, output_dir: str, name: str = 'SpectrogramQueue', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__output_dir = output_dir

    def _put_message(self, message: bytes, addr: tuple[str, int]) -> None:
        spectrogram = message[REQUEST_ID_BYTES_NUMBER + SLICES_NUMBER_BYTES:]
        with open(os.path.join(self.__output_dir, 'SpectrogramQueue - Spectrogram.png'), 'wb') as f:
            f.write(spectrogram)
        super()._put_message(message, addr)


if __name__ == '__main__':
    # SpectrogramQueue().run()
    DebugSpectrogramQueue('../../../debug_files/').run()
