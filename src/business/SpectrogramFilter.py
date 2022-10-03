import os
from io import BytesIO
from socket import socket, AF_INET, SOCK_STREAM
from typing import Callable
from PIL import Image
from config import spectrogram_filter, spectrogram_queue, slice_genre_aggregator
from config.constants import ID_FIELD_SIZE, SLICE_EDGE, SLICES_NUMBER_BYTES
from src.business.abstract_classes.AbstractSyncReceivePipelineStage import AbstractSyncReceivePipelineStage
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper


class SpectrogramFilter(AbstractSyncReceivePipelineStage):
    def __init__(self, name: str = 'SpectrogramFilter', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__server_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__server_socket.bind((spectrogram_filter.HOST, spectrogram_filter.PORT))
        self.__server_socket.listen()
        self._log_func(f'[{self._name}] '
                       f'ServerSocket opened on {spectrogram_filter.HOST}:{spectrogram_filter.PORT}!')

    def _receive_message(self) -> bytes:
        client_socket, addr = self.__server_socket.accept()
        self._log_func(f'[{self._name}] Client connected: {addr}!')
        message = client_socket.receive_message()
        client_socket.close()
        return message

    def _process_message(self, message: bytes) -> bytes:
        song_id = message[:ID_FIELD_SIZE]
        spectrogram = message[ID_FIELD_SIZE:]
        slices_number = self.__get_slices_number(spectrogram)
        slices_number_bytes = slices_number.to_bytes(SLICES_NUMBER_BYTES, 'big', signed=False)
        self._log_func(f'[{self._name}] Received and processed message:'
                       f'\n\tReceived message length: {len(message)}'
                       f'\n\tSongID: {song_id}'
                       f'\n\tSpectrogram length: {len(spectrogram)}'
                       f'\n\tSlices number: {slices_number}'
                       f'\n\tSent message to SliceGenreAggregator length: {len(song_id) + len(slices_number_bytes)}'
                       f'\n\tSent message to SpectrogramQueue length: {len(message) + len(slices_number_bytes)}')
        return song_id + slices_number_bytes + spectrogram

    def _send_message(self, message: bytes) -> None:
        client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        client_socket.connect((slice_genre_aggregator.HOST, slice_genre_aggregator.SLICE_NUMBER_PORT))
        client_socket.send_message(message[:ID_FIELD_SIZE + SLICES_NUMBER_BYTES])
        client_socket.close()

        client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        client_socket.connect((spectrogram_queue.HOST, spectrogram_queue.PUT_PORT))
        client_socket.send_message(message)
        client_socket.close()

    @staticmethod
    def __get_slices_number(spectrogram: bytes) -> int:
        spectrogram = BytesIO(spectrogram)
        spectrogram = Image.open(spectrogram)
        return spectrogram.width // SLICE_EDGE

    def run(self) -> None:
        try:
            AbstractSyncReceivePipelineStage.run(self)
        finally:
            self.__server_socket.close()


class DebugSpectrogramFilter(SpectrogramFilter):
    def __init__(self, output_dir: str, name: str = 'SpectrogramFilter', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__output_dir = output_dir

    def _process_message(self, message: bytes) -> bytes:
        spectrogram = message[ID_FIELD_SIZE:]
        with open(os.path.join(self.__output_dir, 'SpectrogramFilter - Spectrogram.png'), 'wb') as f:
            f.write(spectrogram)

        message = super()._process_message(message)
        return message


if __name__ == '__main__':
    DebugSpectrogramFilter('../../debug_files/').run()
    # SpectrogramFilter().run()
