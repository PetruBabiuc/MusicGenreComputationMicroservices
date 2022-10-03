import os
from typing import Callable
from config.constants import ID_FIELD_SIZE, SLICE_EDGE
from config.rabbit_mq import SLICES_QUEUE, SLICES_DATA_QUEUE
from src.business.abstract_classes.AbstractAsyncReceivePipelineStage import AbstractAsyncReceivePipelineStage
from src.helpers.DnnFactory import DnnFactory
from src.helpers.ImageTransformer import ImageTransformer
from src.helpers.RabbitMqConsumer import RabbitMqConsumer
from src.helpers.RabbitMqProducer import RabbitMqProducer


class SliceGenrePredictor(AbstractAsyncReceivePipelineStage):
    def __init__(self, dnn_path: str,
                 name: str = 'SliceGenrePredictor', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__message_receiver = RabbitMqConsumer(SLICES_QUEUE.name, self._on_received_message)
        self.__message_sender = RabbitMqProducer(SLICES_DATA_QUEUE.exchange, SLICES_DATA_QUEUE.routing_key)
        self.__dnn = DnnFactory().create_dnn(dnn_path)
        self._log_func(f'[{self._name}] Microservice started!')

    def _receive_message(self) -> None:
        self.__message_receiver.receive_message()

    def _process_message(self, message: bytes) -> bytes:
        song_id = message[:ID_FIELD_SIZE]
        slice_data = message[ID_FIELD_SIZE:]
        slice_data = ImageTransformer.transform_image(slice_data, SLICE_EDGE)
        slice_data = [slice_data]
        slice_data = self.__dnn.predict(slice_data)[0]
        probabilities_bytes = slice_data.tobytes()
        self._log_func(f'[{self._name}] Slice processed:'
                       f'\n\tReceived message bytes: {len(message)}'
                       f'\n\tSongID: {song_id}'
                       f'\n\tGenres probabilities: {slice_data}'
                       f'\n\tSent message bytes: {len(song_id) + len(probabilities_bytes)}')
        return song_id + probabilities_bytes

    def _send_message(self, message: bytes) -> None:
        self.__message_sender.send_message(message)


class DebugSliceGenrePredictor(SliceGenrePredictor):
    def __init__(self, dnn_path: str, output_path: str,
                 name: str = 'SliceGenrePredictor', log_func: Callable[[str], None] = print):
        super().__init__(dnn_path, name, log_func)
        self.__output_path = output_path
        self.__current_slice_number = 0

    def _process_message(self, message: bytes) -> bytes:
        with open(os.path.join(self.__output_path,
                               'Slice Genre Predictor - Slices',
                               f'Slice {self.__current_slice_number}.png'), 'wb') as f:
            f.write(message[ID_FIELD_SIZE:])
        self.__current_slice_number += 1
        return super()._process_message(message)


if __name__ == '__main__':
    dnn_relative_path = '../../dnn/musicDNN.tflearn'
    # SliceGenrePredictor(dnn_path).run()
    DebugSliceGenrePredictor(dnn_relative_path, '../../debug_files/').run()
