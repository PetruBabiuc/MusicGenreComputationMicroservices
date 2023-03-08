import os
from typing import Callable
from config.constants import SLICE_EDGE
from config.genre_computer_request_manager import REQUEST_ID_BYTES_NUMBER
from config.rabbit_mq import GenreComputationPipeline
from src.business.abstract_classes.AbstractAsyncReceivePipelineStage import AbstractAsyncReceivePipelineStage
from src.helpers.DnnFactory import DnnFactory
from src.helpers.ImageTransformer import ImageTransformer
from src.helpers.RabbitMqConsumer import RabbitMqConsumer
from src.helpers.RabbitMqProducer import RabbitMqProducer


class SliceGenrePredictor(AbstractAsyncReceivePipelineStage):
    def __init__(self, dnn_path: str,
                 name: str = 'SliceGenrePredictor', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__message_receiver = RabbitMqConsumer(GenreComputationPipeline.SLICES_QUEUE.name,
                                                   self._on_received_message)
        self.__message_sender = RabbitMqProducer(GenreComputationPipeline.SLICES_DATA_QUEUE.exchange,
                                                 GenreComputationPipeline.SLICES_DATA_QUEUE.routing_key)
        self.__dnn = DnnFactory().create_dnn(dnn_path)
        self._log_func(f'[{self._name}] Microservice started!')

    def _start_receiving_messages(self) -> None:
        self.__message_receiver.start_receiving_messages()

    def _process_message(self, message: bytes) -> bytes:
        request_id = message[:REQUEST_ID_BYTES_NUMBER]
        slice_data = message[REQUEST_ID_BYTES_NUMBER:]
        slice_data = ImageTransformer.transform_image(slice_data, SLICE_EDGE)
        slice_data = [slice_data]
        slice_data = self.__dnn.predict(slice_data)[0]
        probabilities_bytes = slice_data.tobytes()
        self._log_func(f'[{self._name}] Slice processed:'
                       f'\n\tReceived message bytes: {len(message)}'
                       f'\n\tRequestID: {request_id}'
                       f'\n\tGenres probabilities: {slice_data}'
                       f'\n\tSent message bytes: {len(request_id) + len(probabilities_bytes)}')
        return request_id + probabilities_bytes

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
            f.write(message[REQUEST_ID_BYTES_NUMBER:])
        self.__current_slice_number += 1
        return super()._process_message(message)


if __name__ == '__main__':
    dnn_relative_path = '../../../dnn/musicDNN.tflearn'
    # SliceGenrePredictor(dnn_path).run()
    DebugSliceGenrePredictor(dnn_relative_path, '../../../debug_files/').run()
