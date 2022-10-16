import os
from io import BytesIO
from socket import socket, AF_INET, SOCK_STREAM
from typing import Callable
from PIL import Image
from config import spectrogram_queue
from config.constants import SLICES_NUMBER_BYTES, SLICE_EDGE
from config.genre_computer_request_manager import REQUEST_ID_BYTES_NUMBER
from config.rabbit_mq import GenreComputationPipeline
from src.business.abstract_classes.AbstractSyncReceivePipelineStage import AbstractSyncReceivePipelineStage
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.RabbitMqProducer import RabbitMqProducer


class SpectrogramSlicer(AbstractSyncReceivePipelineStage):
    def __init__(self, name: str = 'SpectrogramSlicer', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__message_sender = RabbitMqProducer(GenreComputationPipeline.SLICES_QUEUE.exchange,
                                                 GenreComputationPipeline.SLICES_QUEUE.routing_key)
        self._log_func(f'[{self._name}] Microservice started!')

    def _receive_message(self) -> bytes:
        client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        client_socket.connect((spectrogram_queue.HOST, spectrogram_queue.GET_PORT))
        return client_socket.receive_message()

    def _process_message(self, message: bytes) -> bytes:
        request_id = message[:REQUEST_ID_BYTES_NUMBER]
        slice_index = message[REQUEST_ID_BYTES_NUMBER:REQUEST_ID_BYTES_NUMBER + SLICES_NUMBER_BYTES]
        slice_index = int.from_bytes(slice_index, 'big', signed=False)
        spectrogram = message[REQUEST_ID_BYTES_NUMBER + SLICES_NUMBER_BYTES:]
        spectrogram_len = len(spectrogram)
        spectrogram = self.__slice_spectrogram(spectrogram, slice_index)
        self._log_func(f'[{self._name}] Slice created:'
                       f'\n\tReceived message bytes: {len(message)}'
                       f'\n\tRequestID: {request_id}'
                       f'\n\tSliceIndex: {slice_index}'
                       f'\n\tSpectrogram bytes: {spectrogram_len}'
                       f'\n\tSlice bytes: {len(spectrogram)}'
                       f'\n\tSent message bytes: {len(request_id) + len(spectrogram)}')
        return request_id + spectrogram

    def _send_message(self, message: bytes) -> None:
        self.__message_sender.send_message(message)

    @staticmethod
    def __slice_spectrogram(spectrogram: bytes, slice_index: int) -> bytes:
        spectrogram = BytesIO(spectrogram)
        spectrogram = Image.open(spectrogram)

        left = slice_index * SLICE_EDGE
        top = 1  # Because SOX creates spectrogram with 129 (2^n + 1) pixels height
        right = left + SLICE_EDGE
        bottom = SLICE_EDGE + 1
        spectrogram = spectrogram.crop((left, top, right, bottom))

        spectrogram_bytes = BytesIO()
        spectrogram.save(spectrogram_bytes, 'PNG')
        return spectrogram_bytes.getvalue()


class DebugSpectrogramSlicer(SpectrogramSlicer):
    def __init__(self, output_dir: str, name: str = 'SpectrogramSlicer', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__output_dir = output_dir

    def _process_message(self, message: bytes) -> bytes:
        slice_index = message[REQUEST_ID_BYTES_NUMBER:REQUEST_ID_BYTES_NUMBER + SLICES_NUMBER_BYTES]
        slice_index = int.from_bytes(slice_index, 'big', signed=False)
        with open(os.path.join(self.__output_dir, 'Spectrogram Slicer - Spectrogram.png'), 'wb') as f:
            f.write(message[REQUEST_ID_BYTES_NUMBER + SLICES_NUMBER_BYTES:])
        message = super()._process_message(message)
        with open(os.path.join(self.__output_dir,
                               'Spectrogram Slicer - Slices', f'Slice {slice_index}.png'), 'wb') as f:
            f.write(message[REQUEST_ID_BYTES_NUMBER:])
        return message


if __name__ == '__main__':
    # SpectrogramSlicer().run()
    DebugSpectrogramSlicer('../../../debug_files/').run()
