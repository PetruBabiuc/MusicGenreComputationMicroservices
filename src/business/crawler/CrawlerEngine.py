from __future__ import annotations

import json
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable, Any
from urllib.parse import urljoin

import requests

from config import controller
from config.crawler_engine import HOST as CRAWLER_HOST, PORT as CRAWLER_PORT
from config.database import SONG_URLS_PATH, SONG_GENRES_PATH, CRAWLER_STATES_PATH, RESOURCES_URLS_PATH, API_URL_PREFIX
from config.rabbit_mq import Crawler
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers import Base64Converter
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.RabbitMqConsumer import RabbitMqConsumer
from src.helpers.RabbitMqProducer import RabbitMqProducer


class CrawlerEngine(AbstractMicroservice):
    def __init__(self, name: str = 'CrawlerEngine', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)

        # Caching information about genres
        genres = requests.get(API_URL_PREFIX + SONG_GENRES_PATH).json()
        self.__genre_name_to_id = {genre['song_genre_name']: genre['song_genre_id'] for genre in genres}
        self.__genre_id_to_name = {genre['song_genre_id']: genre['song_genre_name'] for genre in genres}

        # Creating RabbitMq producers and consumers
        self.__sender_to_song_url_processors = RabbitMqProducer(Crawler.UrlProcessors.RESTORE_STATE_QUEUE.exchange,
                                                                Crawler.UrlProcessors.RESTORE_STATE_QUEUE.routing_key)
        self.__sender_to_spiders = RabbitMqProducer(Crawler.Spiders.RESTORE_STATE_QUEUE.exchange,
                                                    Crawler.Spiders.RESTORE_STATE_QUEUE.routing_key)
        self.__receiver_from_spiders = RabbitMqConsumer(Crawler.Spiders.RETURN_QUEUE.name,
                                                        self.__on_receive_message_from_spiders)
        self.__receiver_from_song_url_processors = RabbitMqConsumer(Crawler.UrlProcessors.RETURN_QUEUE.name,
                                                                    self.__on_receive_message_from_song_url_processors)

        # Creating ServerSocket for Controller's requests
        self.__server_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        self.__server_socket.bind((CRAWLER_HOST, CRAWLER_PORT))
        self.__server_socket.listen()
        self._log_func(f'[{self._name}] ServerSocket opened for Controller on {CRAWLER_HOST}:{CRAWLER_PORT}')

    def __receive_controller_requests(self) -> None:
        while True:
            con, _ = self.__server_socket.accept()
            Thread(target=self.__handle_controller_request, args=(con,)).start()

    def __handle_controller_request(self, client_socket: HighLevelSocketWrapper) -> None:
        message = client_socket.receive_json_as_dict()
        # Closing socket. Request's response will be delivered asynchronously
        client_socket.close()

        # Getting request data. It will consist only of user's ID. The rest will be in the CrawlerState
        client_id = message['client_id']

        # Getting crawler state. It will be up-to-date because the controller will make a PATCH request to the
        # database API.
        crawler_state = requests.get(f'{API_URL_PREFIX}{CRAWLER_STATES_PATH}/{client_id}').json()
        domain = crawler_state['domain']
        genre_id = crawler_state['desired_genre_id']
        genre = self.__genre_id_to_name[genre_id]
        max_crawled_resources = crawler_state['max_crawled_resources']
        max_computed_genres = crawler_state['max_computed_genres']

        self._log_func(f'[{self._name}] Song request from controller:'
                       f'\n\tClientID: {client_id}'
                       f'\n\tGenre: {genre}'
                       f'\n\tDomain: {domain}'
                       f'\n\tMaxCrawledResources: {max_crawled_resources}'
                       f'\n\tMaxComputedGenres: {max_computed_genres}')

        # If there is already have a song from the desired genre we send it to the controller.
        if self.__send_already_found_song_if_existing(client_id, domain, genre_id):
            return

        # Then, if we have songs found but with undetermined genre, we will try to make use of them.
        # One of them may have the desired genre. We don't check if max_computed_genres is positive because
        # the controller wouldn't forward this request.
        if self.__start_computing_song_genres(client_id, domain, genre):
            return

        # Then, if we didn't have a song with the desired genre and we didn't find any song with the desired
        # genre in the songs (if we had any already found songs at all) we start crawling.
        bloom_filter = dict.get(crawler_state, 'bloom_filter', None)
        self.__start_crawling(client_id, domain, bloom_filter, max_crawled_resources)

    def __send_already_found_song_if_existing(self, client_id: int, domain: str, genre_id: int) -> bool:
        # Getting all the song urls found
        already_found_songs = requests.get(API_URL_PREFIX + SONG_URLS_PATH, params={
            'user_id': client_id,
            'genre_id': genre_id
        }).json()

        for song in already_found_songs:
            # Removing the song from DB
            requests.delete(API_URL_PREFIX + SONG_URLS_PATH, params={'song_url_id': song['song_url_id']})
            absolute_url = urljoin(domain, song['song_url'])
            response = requests.get(absolute_url, allow_redirects=True)
            # The link may not exist be valid anymore
            if not response.ok:
                continue
            song_bytes = response.content
            response = {
                'client_id': client_id,
                'ok': True,
                'song': Base64Converter.bytes_to_string(song_bytes),
                'song_url': song['song_url']
            }
            self.__send_response_to_controller(response)
            return True
        return False

    def __start_computing_song_genres(self, client_id: int, domain: str, genre: str, songs: list[str] = None) -> bool:
        # If the method was called without the parameter songs it is supposed to computing the genres of the songs
        # whose urls are persisted in the DB.
        if songs is None:
            songs = requests.get(API_URL_PREFIX + SONG_URLS_PATH, params={
                'user_id': client_id,
                'genre_id': self.__genre_name_to_id['Computing...']
            }).json()
            songs = [it.song_url for it in songs]
        if len(songs) == 0:
            return False

        message = {
            'client_id': client_id,
            'domain': domain,
            'urls': songs,
            'genre': genre
        }
        message = json.dumps(message).encode()
        self.__sender_to_song_url_processors.send_message(message)
        return True

    @staticmethod
    def __send_response_to_controller(response: dict[str, Any]) -> None:
        client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        client_socket.connect((controller.HOST, controller.CRAWLER_RESPONSES_PORT))
        client_socket.send_dict_as_json(response)
        client_socket.close()

    def __start_crawling(self, client_id: int, domain: str, bloom_filter: str | None,
                         max_crawled_resources: int) -> None:
        queue = requests.get(API_URL_PREFIX + RESOURCES_URLS_PATH, params={'user_id': client_id}).json()

        # Getting up to max_crawled_resources resources so that we don't transfer redundant data
        queue = queue[:max_crawled_resources]

        # Deleting every resource sent to spiders from the DB.
        for resource_url in queue:
            resource_url_id = resource_url['resource_url_id']
            requests.delete(API_URL_PREFIX + RESOURCES_URLS_PATH, params={'resource_url_id': resource_url_id})
        message = {
            'client_id': client_id,
            'domain': domain,
        }
        if len(queue) > 0:
            message['queue'] = queue
        if bloom_filter:
            message['bloom_filter'] = bloom_filter
        message = json.dumps(message)
        self._log_func(f'[{self._name}] Forwarded to spiders:\n\t {message}')
        self.__sender_to_spiders.send_message(message.encode())

    def __on_receive_message_from_spiders(self, message: bytes) -> None:
        message = json.loads(message)
        client_id = message['client_id']
        queue = message['queue']
        songs = message['urls_to_process']

        # If there are more resources to be crawled we update the bloom filter.
        if len(queue) > 0:
            requests.patch(f'{API_URL_PREFIX}{CRAWLER_STATES_PATH}/{client_id}', json={
                'bloom_filter': message['bloom_filter']
            })

        if len(songs) == 0:
            # Telling controller that no song was found.
            self.__send_response_to_controller({'client_id': client_id, 'ok': False})
            # If the spiders found neither song urls nor other resources urls, the domain is completely crawled.
            if len(queue) == 0:
                requests.patch(f'{API_URL_PREFIX}{CRAWLER_STATES_PATH}/{client_id}', json={
                    'finished': True
                })
            return

        # Getting desired genre from the persisted crawler state
        crawler_state = requests.get(f'{API_URL_PREFIX}{CRAWLER_STATES_PATH}/{client_id}').json()

        # Crawler state's max_crawled_resources field.
        requests.patch(f'{API_URL_PREFIX}{CRAWLER_STATES_PATH}/{client_id}', json={
            'max_crawled_resources': crawler_state['max_crawled_resources'] - message['resources_crawled']
        })
        for url in queue:
            requests.post(API_URL_PREFIX + RESOURCES_URLS_PATH, json={
                'user_id': client_id,
                'resource_url': url
            })

        # TODO: Update users_to_services table with message['resources_crawled']
        # Sending songs to the SongUrlProcessors
        genre_id = crawler_state['desired_genre_id']
        genre_name = self.__genre_id_to_name[genre_id]
        self.__start_computing_song_genres(client_id, message['domain'], genre_name, queue)

    def __on_receive_message_from_song_url_processors(self, message: bytes) -> None:
        message = json.loads(message)
        client_id = message['client_id']
        unchecked_urls = dict.get(message, 'unchecked_urls', [])
        genre_to_urls = dict.get(message, 'genre_to_urls', {})

        # Handling songs with genre not computed exactly as they would have their genre computed
        genre_to_urls['Computing...'] = unchecked_urls

        # Persisting every song url
        for genre, songs_urls in genre_to_urls.items():
            genre_id = self.__genre_name_to_id[genre]
            for url in songs_urls:
                requests.post(API_URL_PREFIX, SONG_URLS_PATH, json={
                    'user_id': client_id,
                    'genre_id': genre_id,
                    'song_url': url
                })

        # If song with the desired genre was found return it to controller
        if 'song' in message:
            self.__send_response_to_controller({
                'client_id': client_id,
                'ok': True,
                'song': message['song'],
                'song_url': message['song_url']
            })
            return

        # If no song was from the desired genre, we start crawling again
        # (if max_resources_crawled number is still positive)
        crawler_state = requests.get(f'{API_URL_PREFIX}{CRAWLER_STATES_PATH}/{client_id}').json()
        max_resources_crawled = crawler_state['max_resources_crawled']
        if max_resources_crawled > 0:
            self.__start_crawling(client_id, crawler_state['domain'],
                                  crawler_state['bloom_filter'], max_resources_crawled)
        else:
            # If the crawler crawled through the maximum number of resources,
            # we tell the user that the crawling was finished
            self.__send_response_to_controller({
                'client_id': client_id,
                'ok': False
            })

    def run(self) -> None:
        Thread(target=self.__receiver_from_spiders.start_receiving_messages).start()
        Thread(target=self.__receiver_from_song_url_processors.start_receiving_messages).start()
        self.__receive_controller_requests()


if __name__ == '__main__':
    CrawlerEngine().run()
