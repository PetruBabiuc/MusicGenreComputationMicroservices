from typing import Any, Callable

import requests
from requests import Response

from config.database_api import *


class DatabaseApiProxy:
    def __init__(self, user_name: str = None, password: str = None):
        if user_name is None and password is not None or user_name is not None and password is None:
            raise Exception('The credentials should be either both valid strings or both None.')

        self.__user_name = user_name
        self.__password = password
        self.__jwt = None

        self.__get = self.__wrap_request_function(requests.get)
        self.__post = self.__wrap_request_function(requests.post)
        self.__put = self.__wrap_request_function(requests.put)
        self.__patch = self.__wrap_request_function(requests.patch)
        self.__delete = self.__wrap_request_function(requests.delete)

        if user_name:
            self.__jwt = self.login(user_name, password)
            if not self.__jwt:
                raise Exception('Invalid credentials')

    def __wrap_request_function(self, function: Callable) -> Callable:
        def wrap_function(*args, **kwargs) -> Response:
            args = list(args)
            if not args[0].startswith('http'):
                args[0] = API_URL_PREFIX + args[0]

            if 'headers' in kwargs:
                kwargs['headers']['Authorization'] = f'Bearer {self.__jwt}'
            else:
                kwargs['headers'] = {'Authorization': f'Bearer {self.__jwt}'}

            return function(*args, **kwargs)

        def wrapper_function(*args, **kwargs) -> Response:
            response = wrap_function(*args, **kwargs)
            # Checking if the JWT expired
            if response.status_code == 403:
                self.__jwt = self.login(self.__user_name, self.__password)
                if self.__jwt == '':
                    raise Exception(f'The credentials are no longer valid...')
                response = wrap_function(*args, **kwargs)
                if response.status_code == 403:
                    raise Exception('Forbidden operation')
            return response

        return wrapper_function

    def login(self, user_name: str, password: str) -> str:
        r = self.__post(API_URL_PREFIX + LOGIN_PATH, json={
            'user_name': user_name,
            'password': password
        })
        if not r.ok:
            return ''
        return r.json()['jwt']

    def get_users(self) -> list[dict[str, Any]]:
        response = self.__get(USERS_PATH)
        return response.json()

    def get_genres(self) -> list[dict[str, Any]]:
        return self.__get(SONGS_GENRES_PATH).json()

    def get_services(self, *, service_name: str = None) -> list[dict[str, Any]]:
        kwargs = {}
        if service_name is not None:
            kwargs['params'] = {'service_name': service_name}
        return self.__get(SERVICES_PATH, **kwargs).json()

    def patch_song(self, song_id: int, body: dict[str, Any]) -> Response:
        return self.__patch(SONG_BY_ID_PATH.format(**{
            PathParamNames.SONG_ID: song_id
        }), json=body)

    def get_song_by_id(self, song_id: int) -> dict[str, Any]:
        return self.__get(SONG_BY_ID_PATH.format(**{
            PathParamNames.SONG_ID: song_id
        })).json()

    def increase_user_service_quantity(self, user_id: int, service_id: int, quantity: int) -> Response:
        return self.__patch(USER_BY_ID_SERVICE_BY_ID_PATH.format(**{
            PathParamNames.USER_ID: user_id,
            PathParamNames.SERVICE_ID: service_id
        }), json={
            'op': 'add_quantity',
            'value': quantity
        })

    def get_crawler_state(self, user_id: int) -> dict[str, Any]:
        return self.__get(CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
            PathParamNames.USER_ID: user_id
        })).json()

    def get_bloom_filter(self, user_id: int) -> Response:
        return self.__get(BLOOM_FILTER_PATH.format(**{
            PathParamNames.USER_ID: user_id
        }))

    def get_already_found_songs(self, user_id: int, *, genre_id: int = None) -> list[dict[str, Any]]:
        kwargs = {}
        if genre_id is not None:
            kwargs['params'] = {'genre_id': genre_id}
        return self.__get(SONGS_URLS_PATH.format(**{
            PathParamNames.USER_ID: user_id
        }), **kwargs).json()

    def bulk_delete_songs_urls(self, user_id: int, songs_urls_ids: list[int]) -> Response:
        return self.__post(SONGS_URLS_BULK_DELETE_PATH.format(**{
            PathParamNames.USER_ID: user_id
        }), json=songs_urls_ids)

    def get_songs_urls(self, user_id: int, *, genre_id: int = None) -> list[dict[str, Any]]:
        kwargs = {}
        if genre_id is not None:
            kwargs['params'] = {'genre_id': genre_id}
        return self.__get(SONGS_URLS_PATH.format(**{
                PathParamNames.USER_ID: user_id
            }), **kwargs).json()

    def get_crawler_resources_urls(self, user_id: int, *, limit: int = None) -> list[dict[str, Any]]:
        kwargs = {}
        if limit is not None:
            kwargs['params'] = {'limit': limit}
        return self.__get(CRAWLER_RESOURCES_URLS_PATH.format(**{
            PathParamNames.USER_ID: user_id
        }), **kwargs).json()

    def delete_bloom_filter(self, user_id: int) -> Response:
        return self.__delete(BLOOM_FILTER_PATH.format(**{
                PathParamNames.USER_ID: user_id
            }))

    def bulk_delete_crawler_resources_urls(self, user_id: int, resources_ids: list[int]) -> Response:
        return self.__post(CRAWLER_RESOURCES_URLS_BULK_DELETE_PATH.format(**{
            PathParamNames.USER_ID: user_id
        }), json=resources_ids)

    def patch_crawler_state(self, user_id: int, body: dict[str, Any]) -> Response:
        return self.__patch(CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
                PathParamNames.USER_ID: user_id
            }), json=body)

    def put_bloom_filter(self, user_id: int, bloom_filter: str) -> Response:
        return self.__put(BLOOM_FILTER_PATH.format(**{
                PathParamNames.USER_ID: user_id
            }), json={'value': bloom_filter})

    def bulk_add_crawler_resources_urls(self, user_id: int, resources_urls: list[str]) -> Response:
        return self.__post(CRAWLER_RESOURCES_URLS_BULK_ADD_PATH.format(**{
                PathParamNames.USER_ID: user_id
            }), json=resources_urls)

    def bulk_add_songs_urls(self, user_id: int, genre_id_to_songs_urls: dict[str, list[str]]) -> Response:
        return self.__post(SONGS_URLS_BULK_ADD_PATH.format(**{
            PathParamNames.USER_ID: user_id
        }), json=genre_id_to_songs_urls)

    def post_song(self, user_id: int, song_name: str, genre_id: int) -> Response:
        return self.__post(SONGS_PATH, json={
            'user_id': user_id,
            'song_name': song_name,
            'genre_id': genre_id
        })

    def delete_song(self, song_id: int) -> Response:
        return self.__delete(SONG_BY_ID_PATH.format(**{
                PathParamNames.SONG_ID: song_id
            }))

    def get_crawler_resources_urls_count(self, user_id: int) -> dict[str, Any]:
        return self.__get(CRAWLER_RESOURCES_URLS_COUNT_PATH.format(**{
            PathParamNames.USER_ID: user_id
        })).json()

    def get_crawler_songs_urls_count(self, user_id: int) -> dict[str, Any]:
        return self.__get(SONGS_URLS_COUNT_PATH.format(**{
            PathParamNames.USER_ID: user_id
        })).json()

    def put_crawler_state(self, user_id: int, body: dict[str, Any]) -> Response:
        return self.__put(CRAWLER_GENERAL_STATE_BY_ID_PATH.format(**{
                PathParamNames.USER_ID: user_id
            }), json=body)

    def post_crawler_resource_url(self, user_id: int, url: str) -> Response:
        return self.__post(CRAWLER_RESOURCES_URLS_PATH.format(**{
                PathParamNames.USER_ID: user_id
            }), json={'resource_url': url})

    def post_crawler_song_url(self, user_id: int, song_url: str, genre_id: int) -> Response:
        return self.__post(SONGS_URLS_PATH.format(**{
                PathParamNames.USER_ID: user_id
            }), json={
            'genre_id': genre_id,
            'song_url': song_url
        })

