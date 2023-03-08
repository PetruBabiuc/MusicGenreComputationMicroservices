import os
import shlex
from io import BytesIO
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import Popen, PIPE
from typing import Callable

from mutagen.mp3 import MP3, MPEGInfo

from config import spectrogram_filter
from config.constants import PIXELS_PER_SECOND
from config.genre_computer_request_manager import REQUEST_ID_BYTES_NUMBER
from config.rabbit_mq import GenreComputationPipeline
from src.business.abstract_classes.AbstractAsyncReceivePipelineStage import AbstractAsyncReceivePipelineStage
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.RabbitMqConsumer import RabbitMqConsumer


class SpectrogramMaker(AbstractAsyncReceivePipelineStage):
    def __init__(self, name: str = 'SpectrogramMaker', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__message_receiver = RabbitMqConsumer(GenreComputationPipeline.SONGS_QUEUE.name, self._on_received_message)
        self._log_func(f'[{self._name}] Microservice started!')

    def _start_receiving_messages(self) -> None:
        self.__message_receiver.start_receiving_messages()

    def _process_message(self, message: bytes) -> bytes:
        request_id = message[:REQUEST_ID_BYTES_NUMBER]
        song = message[REQUEST_ID_BYTES_NUMBER:]
        song_info = self.__get_song_info(song)
        message_len = len(message)
        message = self.__create_spectrogram(song, song_info.channels, int(song_info.length))
        self._log_func(f'[{self._name}] Message received and processed:'
                       f'\n\tReceived message bytes: {message_len}'
                       f'\n\tRequestID: {request_id}'
                       f'\n\tSong bytes: {len(song)}'
                       f'\n\tSong channels number: {song_info.channels}'
                       f'\n\tSong duration: {int(song_info.length)} seconds'
                       f'\n\tSpectrogram bytes: {len(message)}'
                       f'\n\tSent message bytes: {len(message) + len(request_id)}')
        return request_id + message

    def _send_message(self, message: bytes) -> None:
        client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        client_socket.connect((spectrogram_filter.HOST, spectrogram_filter.PORT))
        client_socket.send_message(message)
        client_socket.close()

    @staticmethod
    def __get_song_info(song: bytes) -> MPEGInfo:
        song = BytesIO(song)
        song = MP3(song)
        return song.info

    def __create_spectrogram(self, song: bytes, channels: int, seconds_duration: int) -> bytes:
        command = 'sox -t mp3 - -n '
        if channels > 1:
            command += 'remix - '
        command += f'spectrogram -X {PIXELS_PER_SECOND} -Y 200 -d {seconds_duration} -m -r -o -'
        command = shlex.split(command)
        p = Popen(command, stdin=PIPE, stdout=PIPE)
        output, errors = p.communicate(song)
        if errors:
            self._log_func(f'[{self._name}] {errors.decode()}')
        return output


class DebugSpectrogramMaker(SpectrogramMaker):
    def __init__(self, output_dir: str, name: str = 'SpectrogramMaker', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__output_dir = output_dir

    def _process_message(self, message: bytes) -> bytes:
        song = message[REQUEST_ID_BYTES_NUMBER:]
        with open(os.path.join(self.__output_dir, 'SpectrogramMaker - Song.mp3'), 'wb') as f:
            f.write(song)

        message = super()._process_message(message)
        spectrogram = message[REQUEST_ID_BYTES_NUMBER:]
        with open(os.path.join(self.__output_dir, 'SpectrogramMaker - Spectrogram.png'), 'wb') as f:
            f.write(spectrogram)

        return message


if __name__ == '__main__':
    DebugSpectrogramMaker('../../../debug_files/').run()
    # SpectrogramMaker().run()
