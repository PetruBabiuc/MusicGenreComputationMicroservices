from socket import socket, SOCK_STREAM, AF_INET
from typing import Callable
from numpy import frombuffer, ndarray, argmax, float32
from config import slice_genre_aggregator
from config.dnn import GENRES
from config.genre_computer_request_manager import REQUEST_ID_BYTES_NUMBER
from config.rabbit_mq import GenreComputationPipeline
from src.business.abstract_classes.AbstractAsyncReceivePipelineStage import AbstractAsyncReceivePipelineStage
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.RabbitMqConsumer import RabbitMqConsumer


class SliceDataProcessor(AbstractAsyncReceivePipelineStage):
    def __init__(self, name: str = 'SliceDataProcessor', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__message_receiver = RabbitMqConsumer(GenreComputationPipeline.SLICES_DATA_QUEUE.name,
                                                   self._on_received_message)
        self._log_func(f'[{self._name}] Microservice started!')

    def _start_receiving_messages(self) -> None:
        self.__message_receiver.start_receiving_messages()

    def _process_message(self, message: bytes) -> bytes:
        request_id = message[:REQUEST_ID_BYTES_NUMBER]
        slice_data = message[REQUEST_ID_BYTES_NUMBER:]
        slice_data = frombuffer(slice_data, dtype=float32)
        genre = self.__get_genre(slice_data)
        message_to_send = request_id + genre.encode()
        self._log_func(f'[{self._name}] Received and processed message:'
                       f'\n\tReceived message bytes: {len(message)}'
                       f'\n\tRequestID: {request_id}'
                       f'\n\tSlice data: {slice_data}'
                       f'\n\tGenre: {genre}'
                       f'\n\tSent message bytes: {len(message_to_send)}')
        return message_to_send

    @staticmethod
    def __get_genre(song_data: ndarray) -> str:
        max_ind = argmax(song_data)
        return GENRES[max_ind]

    def _send_message(self, message: bytes) -> None:
        client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        client_socket.connect((slice_genre_aggregator.HOST, slice_genre_aggregator.SLICE_GENRE_PORT))
        client_socket.send_message(message)
        client_socket.close()


if __name__ == '__main__':
    SliceDataProcessor().run()
