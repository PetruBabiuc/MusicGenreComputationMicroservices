from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable

from config import controller, constants, genre_computer_request_manager
from config.redis import CONTROLLER_TOPIC
from src.helpers import Base64Converter
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.Mp3ValidatorProxy import Mp3ValidatorProxy
from src.helpers.SocketJsonMessageAwaiter import SocketJsonMessageAwaiter
from src.presentation.abstract_classes.AbstractFastApiController import AbstractFastApiController
from src.presentation.song_adder_controller.routes.SongRoutes import SongRoutes


class SongAdderController(AbstractFastApiController):
    def __init__(self, name: str = 'SongAdderController', log_func: Callable[[str], None] = print):
        self.__genre_computation_results_awaiter: SocketJsonMessageAwaiter[int] = SocketJsonMessageAwaiter(
            controller.HOST, controller.GENRE_COMPUTATION_PORT, 'song_id')

        log_func(f'[{name}] ServerSocket for computation results '
                 f'opened on {controller.HOST}:{controller.GENRE_COMPUTATION_PORT}!')

        self.__mp3_validator_proxy = Mp3ValidatorProxy(CONTROLLER_TOPIC, 'song_id')

        song_routes = SongRoutes(self.__check_if_song_is_valid, self.__compute_genre)

        super().__init__([song_routes], name, controller.HOST, controller.CLIENT_PORT, log_func)

    def __check_if_song_is_valid(self, song_id: int, song_bytes: bytes) -> bool:
        base64_string_song = Base64Converter.bytes_to_string(song_bytes)
        return self.__mp3_validator_proxy.validate_song({
            'song_id': song_id,
            'song': base64_string_song,
            'source': 'Controller'
        })

    def __compute_genre(self, song_id: int, song_bytes: bytes) -> dict:
        # Putting awaitable genre computation
        self.__genre_computation_results_awaiter.put_awaitable(song_id)

        # Forwarding the genre computation request
        self.__forward_genre_computation_request(song_id, song_bytes)

        # Awaiting genre computation
        message = self.__genre_computation_results_awaiter.await_result(song_id)

        return message

    def __forward_genre_computation_request(self, song_id: int, song_bytes: bytes) -> None:
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

    def run(self) -> None:
        Thread(target=self.__genre_computation_results_awaiter.start_receiving_responses).start()
        self._log_func(f'[{self._name}] Started receiving genre computation results on '
                       f'{controller.HOST}:{controller.GENRE_COMPUTATION_PORT}')
        super().run()


if __name__ == '__main__':
    SongAdderController().run()
