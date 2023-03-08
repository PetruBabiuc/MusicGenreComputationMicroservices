from __future__ import annotations

import json
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Callable, Any
from urllib.parse import urljoin

import requests

import config.crawler_management_controller
from config.constants import LOGGED_URLS, REQUEST_TIMEOUT
from config.crawler_engine import HOST as CRAWLER_HOST, PORT as CRAWLER_PORT
from config.database_api_credentials import MICROSERVICE_CREDENTIALS
from config.rabbit_mq import Crawler
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers import Base64Converter
from src.helpers.DatabaseApiProxy import DatabaseApiProxy
from src.helpers.HighLevelSocketWrapper import HighLevelSocketWrapper
from src.helpers.RabbitMqConsumer import RabbitMqConsumer
from src.helpers.RabbitMqProducer import RabbitMqProducer


class CrawlerEngine(AbstractMicroservice):
    def __init__(self, name: str = 'CrawlerEngine', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)

        self.__database_proxy = DatabaseApiProxy(*MICROSERVICE_CREDENTIALS)

        # Caching information about genres
        genres = self.__database_proxy.get_genres()
        # TODO: REMOVE OLD CODE
        # genres = requests.get(API_URL_PREFIX + SONGS_GENRES_PATH).json()
        self.__genre_name_to_id = {genre['song_genre_name']: genre['song_genre_id'] for genre in genres}
        self.__genre_id_to_name = {genre['song_genre_id']: genre['song_genre_name'] for genre in genres}

        # Caching information about 'crawled_resource' service
        self.__crawled_resource_service_id = self.__database_proxy.get_services(
            service_name='crawled_resource'
        )[0]['service_id']

        # TODO: REMOVE OLD CODE
        # self.__crawled_resource_service_id = self.__crawled_resource_service_id = requests.get(
        #     API_URL_PREFIX + SERVICES_PATH, params={
        #         'service_name': 'crawled_resource'
        #     }).json()[0]['service_id']

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
        # database_scripts API.

        # TODO: REMOVE OLD CODE
        crawler_state = self.__database_proxy.get_crawler_state(client_id)

        # crawler_state = requests.get(API_URL_PREFIX + CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
        #     PathParamNames.USER_ID: client_id})).json()
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
        # TODO: REMOVE OLD CODE
        response = self.__database_proxy.get_bloom_filter(client_id)
        # response = requests.get(API_URL_PREFIX + BLOOM_FILTER_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # }))
        bloom_filter = response.json()['value'] if response.ok else None
        self.__start_crawling(client_id, domain, bloom_filter, max_crawled_resources, max_computed_genres)

    def __send_already_found_song_if_existing(self, client_id: int, domain: str, genre_id: int) -> bool:
        # Getting all the song urls found

        # TODO: REMOVE OLD CODE
        already_found_songs = self.__database_proxy.get_already_found_songs(client_id, genre_id=genre_id)
        # already_found_songs = requests.get(API_URL_PREFIX + SONGS_URLS_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # }), params={
        #     'genre_id': genre_id
        # }).json()

        songs_urls_ids_to_remove = []
        found = False
        for index, song in enumerate(already_found_songs):
            # Removing the song from DB
            songs_urls_ids_to_remove.append(song['song_url_id'])
            absolute_url = urljoin(domain, song['song_url'])
            response = requests.get(absolute_url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
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
            self._log_func(f'[{self._name}]'
                           f'\n\tClientID: {client_id}'
                           f'\n\tEvent: Song found!'
                           f'\n\tSong URL: {absolute_url}')
            found = True
            break
        # TODO: REMOVE OLD CODE
        self.__database_proxy.bulk_delete_songs_urls(client_id, songs_urls_ids_to_remove)
        # requests.post(API_URL_PREFIX + SONGS_URLS_BULK_DELETE_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # }), json=songs_urls_ids_to_remove)
        if not found:
            self._log_func(f'[{self._name}]'
                           f'\n\tClientID: {client_id}'
                           f'\n\tEvent: No song with the desired genre and that had URL already persisted was found')
        return found

    def __start_computing_song_genres(self, client_id: int, domain: str, genre: str, songs: list[str] = None) -> bool:
        # If the method was called without the parameter songs it is supposed to computing the genres of the songs
        # whose urls are persisted in the DB.
        if songs is None:
            # TODO: REMOVE OLD CODE
            songs = self.__database_proxy.get_songs_urls(
                client_id, genre_id=self.__genre_name_to_id['Computing...'])
            # songs = requests.get(API_URL_PREFIX + SONGS_URLS_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # }), params={
            #     'genre_id': self.__genre_name_to_id['Computing...']
            # }).json()

            # TODO: REMOVE OLD CODE
            self.__database_proxy.bulk_delete_songs_urls(client_id, [song['song_url_id'] for song in songs])
            # requests.post(API_URL_PREFIX + SONGS_URLS_BULK_DELETE_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # }), json=[song['song_url_id'] for song in songs])
            songs = [it['song_url'] for it in songs]
        if len(songs) == 0:
            self._log_func(f'[{self._name}]'
                           f'\n\tClientID: {client_id}'
                           f'\n\tEvent: No song found for genre computation...')
            return False

        message = {
            'client_id': client_id,
            'domain': domain,
            'urls': songs,
            'genre': genre
        }
        message = json.dumps(message).encode()
        self._log_func(f'[{self._name}]'
                       f'\n\tClientID: {client_id}'
                       f'\n\tEvent: Started genre computation of songs already found'
                       f'\n\tSongs:'
                       f'\n\t\tCount: {len(songs)}'
                       f'\n\t\tURLs: {songs[:LOGGED_URLS]} ... {songs[-LOGGED_URLS:]}')
        self.__sender_to_song_url_processors.send_message(message)
        return True

    def __send_response_to_controller(self, response: dict[str, Any]) -> None:
        client_socket = HighLevelSocketWrapper(socket(AF_INET, SOCK_STREAM))
        client_socket.connect((config.crawler_management_controller.HOST,
                               config.crawler_management_controller.CRAWLER_RESPONSES_PORT))
        client_socket.send_dict_as_json(response)
        client_socket.close()
        response_to_print = dict(response)
        if 'song' in response_to_print:
            response_to_print['song'] = f'{len(response_to_print["song"])} Base64 characters...'
        self._log_func(f'[{self._name}]'
                       f'\n\tClientID: {response["client_id"]}'
                       f'\n\tEvent: Response for controller: {response_to_print}')

    def __start_crawling(self, client_id: int, domain: str, bloom_filter: str | None,
                         max_crawled_resources: int, max_computed_genres: int) -> None:
        # Getting up to max_crawled_resources resources so that we don't transfer redundant data
        # max_crawled_resources takes 0 as value when crawling the entire domain (debug only)
        params = {}
        if max_crawled_resources > 0:
            params['limit'] = max_crawled_resources

        # TODO: REMOVE OLD CODE
        queue = self.__database_proxy.get_crawler_resources_urls(client_id, **params)
        # queue = requests.get(API_URL_PREFIX + CRAWLER_RESOURCES_URLS_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # }), params=params).json()
        if len(queue) == 0:
            self._log_func(f'[{self._name}]'
                           f'\n\tClientID: {client_id}'
                           f'\n\tTrying to crawl the domain that has no resources to crawl left...')
            # TODO: REMOVE OLD CODE
            self.__database_proxy.delete_bloom_filter(client_id)
            # requests.delete(API_URL_PREFIX + BLOOM_FILTER_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # }))
            self.__send_response_to_controller({
                'client_id': client_id,
                'ok': False,
                'no_more_resources_to_crawl': True
            })
            return

        # Deleting every resource sent to spiders from the DB.
        resources_ids = [it['resource_url_id'] for it in queue]
        # TODO: REMOVE OLD CODE
        self.__database_proxy.bulk_delete_crawler_resources_urls(client_id, resources_ids)
        # requests.post(API_URL_PREFIX + CRAWLER_RESOURCES_URLS_BULK_DELETE_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # }), json=resources_ids)
        message = {
            'client_id': client_id,
            'domain': domain,
            'max_crawled_resources': max_crawled_resources,
            # max_found_items =
            #   0 => as many as possible
            #   1 => just one (minimises user's costs)
            #   max_computed_genres => if getting song's genre from ID3 metadata would count as genre computation
            #       this will minimise both user's cost and resources' usage
            'max_found_items': 1
        }
        message_to_print = dict(message)
        queue = [it['resource_url'] for it in queue]
        if len(queue) > 0:
            message['queue'] = queue
            message_to_print['queue'] = {
                'count': len(queue),
                'URLs': f"{queue[:LOGGED_URLS]} ... {queue[-LOGGED_URLS:]}"
            }
        if bloom_filter:
            message['bloom_filter'] = bloom_filter
            message_to_print['bloom_filter'] = f'Base64 string containing {len(bloom_filter)} characters...'

        self._log_func(f'[{self._name}]'
                       f'\n\tClientID: {client_id}'
                       f'\n\tEvent: Forwarded to spiders'
                       f'\n\tMessage: {message_to_print}')

        message = json.dumps(message)
        self.__sender_to_spiders.send_message(message.encode())

    def __on_receive_message_from_spiders(self, message: bytes) -> None:
        message = json.loads(message)
        client_id = message['client_id']
        queue = message['queue']
        songs = message['urls_to_process']

        # Updating the quantity of 'crawled_resource' service used by the user
        # TODO: REMOVE OLD CODE
        self.__database_proxy.increase_user_service_quantity(
            client_id, self.__crawled_resource_service_id, message['resources_crawled'])
        # requests.patch(API_URL_PREFIX + USER_BY_ID_SERVICE_BY_ID_PATH.format(**{
        #     PathParamNames.USER_ID: client_id,
        #     PathParamNames.SERVICE_ID: self.__crawled_resource_service_id
        # }), json={
        #     'op': 'add_quantity',
        #     'value': message['resources_crawled']
        # })

        # Getting desired genre from the persisted crawler state
        # TODO: REMOVE OLD CODE
        crawler_state = self.__database_proxy.get_crawler_state(client_id)
        # crawler_state = requests.get(API_URL_PREFIX + CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # })).json()

        # If there are more resources to be crawled we update the bloom filter.
        # TODO: REMOVE OLD CODE
        resources_urls = self.__database_proxy.get_crawler_resources_urls(client_id)
        # resources_urls = requests.get(API_URL_PREFIX + CRAWLER_RESOURCES_URLS_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # })).json()
        if len(queue) > 0 or len(resources_urls) > 0:
            # TODO: REMOVE OLD CODE
            self.__database_proxy.patch_crawler_state(client_id, {
                'max_crawled_resources': crawler_state['max_crawled_resources'] - message['resources_crawled']
            })
            # requests.patch(API_URL_PREFIX + CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # }), json={
            #     'max_crawled_resources': crawler_state['max_crawled_resources'] - message['resources_crawled']
            # })

            # TODO: REMOVE OLD CODE
            self.__database_proxy.put_bloom_filter(client_id, message['bloom_filter'])
            # requests.put(API_URL_PREFIX + BLOOM_FILTER_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # }), json={'value': message['bloom_filter']})

            # Inserting the new resources urls in the DB.
            # TODO: REMOVE OLD CODE
            self.__database_proxy.bulk_add_crawler_resources_urls(client_id, queue)
            # requests.post(API_URL_PREFIX + CRAWLER_RESOURCES_URLS_BULK_ADD_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # }), json=queue)

        if len(songs) == 0:
            # Telling controller that no song was found.
            self.__send_response_to_controller({'client_id': client_id, 'ok': False})
            self._log_func(f'[{self._name}]'
                           f'\n\tClientID: {client_id}'
                           f'\n\tEvent: No song found by the spiders...')

        # Sending songs to the SongUrlProcessors
        genre_id = crawler_state['desired_genre_id']
        genre_name = self.__genre_id_to_name[genre_id]
        self._log_func(f'[{self._name}]'
                       f'\n\tClientID: {client_id}'
                       f'\n\tEvent: Songs were found by the spiders!'
                       f'\n\tSongs to route to the UrlProcessors:'
                       f'\n\t\tCount: {len(songs)}'
                       f'\n\t\tURLs: {songs[:LOGGED_URLS]} ... {songs[-LOGGED_URLS:]}')
        self.__start_computing_song_genres(client_id, message['domain'], genre_name, songs)

    def __on_receive_message_from_song_url_processors(self, message: bytes) -> None:
        message = json.loads(message)
        client_id = message['client_id']
        unchecked_urls = dict.get(message, 'unchecked_urls', [])
        genre_to_urls = dict.get(message, 'genre_to_urls', {})

        # Handling songs with genre not computed exactly as they would have their genre computed
        if 'Computing...' not in genre_to_urls:
            genre_to_urls['Computing...'] = []
        genre_to_urls['Computing...'].extend(unchecked_urls)

        # Persisting every song url
        # TODO: REMOVE OLD CODE
        self.__database_proxy.bulk_add_songs_urls(client_id, {
            str(self.__genre_name_to_id[genre]): song_urls for genre, song_urls in genre_to_urls.items()
        })
        # requests.post(API_URL_PREFIX + SONGS_URLS_BULK_ADD_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # }), json={
        #     str(self.__genre_name_to_id[genre]): song_urls for genre, song_urls in genre_to_urls.items()
        # })

        # If song with the desired genre was found return it to controller
        if 'song' in message:
            self.__send_response_to_controller({
                'client_id': client_id,
                'ok': True,
                'song': message['song'],
                'song_url': message['song_url']
            })
            self._log_func(f'[{self._name}]'
                           f'\n\tClientID: {client_id}'
                           f'\n\tEvent: Song found by the UrlProcessors: {message["song_url"]}')
            return

        # If no song was from the desired genre, we start crawling again
        # (if max_resources_crawled number is still positive)
        # TODO: REMOVE OLD CODE
        crawler_state = self.__database_proxy.get_crawler_state(client_id)
        # crawler_state = requests.get(API_URL_PREFIX + CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
        #     PathParamNames.USER_ID: client_id
        # })).json()
        max_crawled_resources = crawler_state['max_crawled_resources']
        max_computed_genres = crawler_state['max_computed_genres']
        if max_crawled_resources > 0 and max_computed_genres > 0:
            self._log_func(f'[{self._name}]'
                           f'\n\tClientID: {client_id}'
                           f'\n\tEvent: No song found with the desired genre found by the UrlProcessors...'
                           f'\n\tAction taken: Started crawling again...')
            # TODO: REMOVE OLD CODE
            response = self.__database_proxy.get_bloom_filter(client_id)
            # response = requests.get(API_URL_PREFIX + BLOOM_FILTER_PATH.format(**{
            #     PathParamNames.USER_ID: client_id
            # }))
            bloom_filter = response.json()['value'] if response.ok else None
            self.__start_crawling(client_id, crawler_state['domain'],
                                  bloom_filter, max_crawled_resources, max_computed_genres)
        else:
            # If the crawler crawled through the maximum number of resources,
            # we tell the user that the crawling was finished
            self._log_func(f'[{self._name}]'
                           f'\n\tClientID: {client_id}'
                           f'\n\tEvent: No song found with the desired genre found by the UrlProcessors...'
                           f'\n\tAction taken: max_resources_crawled and/or max_computed_genres reached, '
                           f'returning no song for the Controller...')
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
