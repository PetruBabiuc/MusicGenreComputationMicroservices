import os.path
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable, Any
from urllib.parse import urlparse

from config import constants, controller, genre_computer_request_manager, crawler_engine
from config.database_api_credentials import MICROSERVICE_CREDENTIALS
from config.redis import CONTROLLER_TOPIC
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers import Base64Converter
from src.helpers.DatabaseApiProxy import DatabaseApiProxy
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.Mp3ValidatorProxy import Mp3ValidatorProxy
from src.helpers.SocketJsonMessageAwaiter import SocketJsonMessageAwaiter


class Controller(AbstractMicroservice):
    def __init__(self, name: str = 'Controller', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)

        self.__client_server_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__client_server_socket.bind((controller.HOST, controller.CLIENT_PORT))
        self.__client_server_socket.listen()
        self._log_func(f'[{self._name}] ServerSocket for clients '
                       f'opened on {controller.HOST}:{controller.CLIENT_PORT}!')

        self.__genre_computation_results_awaiter: SocketJsonMessageAwaiter[int] = SocketJsonMessageAwaiter(
            controller.HOST, controller.GENRE_COMPUTATION_PORT, 'song_id')

        self.__crawling_results_awaiter: SocketJsonMessageAwaiter[int] = SocketJsonMessageAwaiter(
            controller.HOST, controller.CRAWLER_RESPONSES_PORT, 'client_id'
        )

        self.__mp3_validator_proxy = Mp3ValidatorProxy(CONTROLLER_TOPIC, 'song_id')

        self.__database_proxy = DatabaseApiProxy(*MICROSERVICE_CREDENTIALS)

        self._log_func(f'[{self._name}] ServerSocket for computation results '
                       f'opened on {controller.HOST}:{controller.GENRE_COMPUTATION_PORT}!')

        # Caching information about genres
        # TODO: REMOVE OLD CODE
        genres = self.__database_proxy.get_genres()
        # genres = requests.get(API_URL_PREFIX + SONGS_GENRES_PATH).json()
        self.__genre_name_to_id = {genre['song_genre_name']: genre['song_genre_id'] for genre in genres}

    def __serve_client(self, client_socket: HighLevelSocketWrapper, addr: tuple[str, int]) -> None:
        message = client_socket.receive_json_as_dict()
        operation = message['operation']

        if operation == 'compute_genre':
            self.__handle_genre_computation_request(client_socket, message)
        elif operation == 'crawl':
            self.__handle_crawl_request(client_socket, message)

        client_socket.close()

    def __handle_genre_computation_request(self, client_socket: HighLevelSocketWrapper,
                                           message: dict[str, Any]) -> None:
        # TODO: get client_id from session (here or in the React/Angular frontend proxy)
        client_id = message['client_id']

        # Inserting song row in the DB
        # TODO: REMOVE OLD CODE
        response = self.__database_proxy.post_song(
            client_id, message['song_name'], self.__genre_name_to_id['Computing...']).json()
        # response = requests.post(API_URL_PREFIX + SONGS_PATH, json={
        #     'user_id': client_id,
        #     'song_name': message['song_name'],
        #     'genre_id': self.__genre_name_to_id['Computing...']
        # }).json()
        song_id = response['song_id']

        song = message['song']

        if not self.__check_if_song_is_valid(song, song_id):
            self._log_func(f'[{self._name}] Invalid MP3 from UserID = {client_id}...')

            # TODO: REMOVE OLD CODE
            self.__database_proxy.delete_song(song_id)
            # requests.delete(API_URL_PREFIX + SONG_BY_ID_PATH.format(**{
            #     PathParamNames.SONG_ID: song_id
            # }))
            client_socket.send_dict_as_json({'status': 'Invalid MP3'})
            return

        song = Base64Converter.string_to_bytes(song)

        self.__genre_computation_results_awaiter.put_awaitable(song_id)

        # Sending song for genre computation
        self._compute_song_genre(song_id, song)

        # Awaiting genre computation
        message = self.__genre_computation_results_awaiter.await_result(song_id)

        client_socket.send_dict_as_json(message)

    def __check_if_song_is_valid(self, base64_string_song: str, song_id: int) -> bool:
        return self.__mp3_validator_proxy.validate_song({
            'song_id': song_id,
            'song': base64_string_song,
            'source': 'Controller'
        })

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

    def __check_if_crawling_is_finished(self, client_id: int) -> bool:
        # TODO: REMOVE OLD CODE
        response = self.__database_proxy.get_crawler_resources_urls_count(client_id)
        # response = requests.get(API_URL_PREFIX + CRAWLER_RESOURCES_URLS_COUNT_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # })).json()
        if response['count'] > 0:
            return False

        # TODO: REMOVE OLD CODE
        response = self.__database_proxy.get_crawler_songs_urls_count(client_id)
        # response = requests.get(API_URL_PREFIX + SONGS_URLS_COUNT_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # })).json()
        if response['count'] > 0:
            return False

        # TODO: REMOVE OLD CODE
        self.__database_proxy.patch_crawler_state(client_id, {'finished': True})
        # requests.patch(API_URL_PREFIX + CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # }), json={'finished': True})

        # TODO: REMOVE OLD CODE
        self.__database_proxy.delete_bloom_filter(client_id)
        # requests.delete(API_URL_PREFIX + BLOOM_FILTER_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # }))
        return True

    def __serve_client_task(self):
        while True:
            client_socket, addr = self.__client_server_socket.accept()
            self._log_func(f'[{self._name}] Client connected: {addr}')
            Thread(target=self.__serve_client, args=(client_socket, addr)).start()

    def run(self) -> None:
        try:
            Thread(target=self.__crawling_results_awaiter.start_receiving_responses).start()
            Thread(target=self.__genre_computation_results_awaiter.start_receiving_responses).start()
            self.__serve_client_task()
        finally:
            self.__client_server_socket.close()

    def __handle_crawl_request(self, client_socket: HighLevelSocketWrapper, message: dict[str, Any]):
        # TODO: make that a client can have at most one request being handled at once
        client_id = message['client_id']
        genre_id = message['genre_id']
        body = {
            'max_crawled_resources': message['max_crawled_resources'],
            'max_computed_genres': message['max_computed_genres'],
            'desired_genre_id': genre_id
        }
        if 'domain' in message:
            # TODO: Check if domain is a valid URL
            # Start crawling a new domain
            parsed_domain = urlparse(message['domain'])
            body['domain'] = f'{parsed_domain.scheme}://{parsed_domain.netloc}/'
            # Adding/overwriting crawler state
            # TODO: REMOVE OLD CODE
            self.__database_proxy.put_crawler_state(client_id, body)
            # requests.put(API_URL_PREFIX + CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # }), json=body)
            # Adding seed url
            # TODO: REMOVE OLD CODE
            self.__database_proxy.post_crawler_resource_url(client_id, parsed_domain.path)
            # requests.post(API_URL_PREFIX + CRAWLER_RESOURCES_URLS_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # }), json={
            #     'resource_url': parsed_domain.path
            # })
        else:
            # New crawling request on the same domain
            # TODO: REMOVE OLD CODE
            # if requests.get(API_URL_PREFIX + CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # })).json()['finished']:
            if self.__database_proxy.get_crawler_state(client_id)['finished']:
                self._log_func(f'[{self._name}] Invalid crawling attempt:'
                               f'\n\tClientID: {client_id}'
                               f'\n\tDomain already finished crawling...')
                client_socket.send_dict_as_json({
                    'ok': False,
                    'finished': True
                })
                client_socket.close()
                return
            # TODO: REMOVE OLD CODE
            self.__database_proxy.patch_crawler_state(client_id, body)
            # requests.patch(API_URL_PREFIX + CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # }), json=body)

        self.__crawling_results_awaiter.put_awaitable(client_id)

        # Forwarding the request to the crawler
        crawler_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        crawler_socket.connect((crawler_engine.HOST, crawler_engine.PORT))
        crawler_socket.send_dict_as_json({'client_id': client_id})
        crawler_socket.close()

        result = self.__crawling_results_awaiter.await_result(client_id)

        if self.__check_if_crawling_is_finished(client_id):
            result['finished'] = True

        # No song found...
        if not result['ok']:
            client_socket.send_dict_as_json(result)
            return

        # A song was found.
        # If the client doesn't receive it successfully, the song's url will be stored in the DB.
        try:
            client_socket.send_dict_as_json(result)
        except BaseException:
            # TODO: REMOVE OLD CODE
            self.__database_proxy.post_crawler_song_url(client_id, result['song_url'], genre_id)
            # requests.post(API_URL_PREFIX + SONGS_URLS_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # }), json={
            #     'genre_id': genre_id,
            #     'song_url': result['song_url']
            # })


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
