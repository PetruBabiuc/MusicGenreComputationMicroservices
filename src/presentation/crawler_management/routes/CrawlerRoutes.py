import time
from typing import Callable
from urllib.parse import urlparse

from classy_fastapi import post, get
from fastapi import Depends, HTTPException
from functional import seq
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_403_FORBIDDEN, HTTP_428_PRECONDITION_REQUIRED, HTTP_404_NOT_FOUND, HTTP_423_LOCKED

import config.crawler_management_controller as api_paths
from config.database_api_credentials import MICROSERVICE_CREDENTIALS
from config.user_types import USER
from src.helpers import Base64Converter
from src.helpers.DatabaseApiProxy import DatabaseApiProxy
from src.helpers.SynchronizedSet import SynchronizedSet
from src.model.dto.StartCrawlingRequest import StartCrawlingRequest
from src.presentation.abstract_classes.routes.AbstractSecuredRoutable import AbstractSecuredRoutable


class CrawlerRoutes(AbstractSecuredRoutable):
    def __init__(self, crawl_func: Callable[[int], dict], name: str, log_func: Callable[[str], None] = print) -> None:
        super().__init__()

        self.__crawl_func = crawl_func
        self.__log_func = log_func
        self.__name = name

        self.__users_crawling: SynchronizedSet[int] = SynchronizedSet()
        self.__database_proxy = DatabaseApiProxy(*MICROSERVICE_CREDENTIALS)

    @get(api_paths.CRAWLER_STATUS_PATH)
    def crawler_status(self, token: str = Depends(AbstractSecuredRoutable.OAUTH2_SCHEME)):
        user_id = self.__get_user_id(token)

        # The domain is the only thing that the user should know from what the Database API returns
        try:
            domain = self.__database_proxy.get_crawler_state(user_id)['domain']
            resources_urls_count = self.__database_proxy.get_crawler_resources_urls_count(user_id)['count']

            # Ex: [{'song_url_id': 1, 'song_url': '/URL', 'genre_id': 2}]
            genre_id_to_songs_count = self.__database_proxy.get_songs_urls(user_id)

            # Ex: [{'genre_id': 2, 'count': 1}]
            genre_id_to_songs_count = seq(genre_id_to_songs_count)\
                .group_by(lambda it: it['genre_id'])\
                .map(lambda pair: {'genre_id': pair[0], 'count': len(pair[1])})\
                .to_list()

            with self.__users_crawling as users_crawling:
                is_started = user_id in users_crawling

            response = {
                'is_started': is_started,
                'domain': domain,
                'resources_urls_count': resources_urls_count,
                'genre_id_to_songs_count': genre_id_to_songs_count
            }
            return response
        except KeyError:
            raise HTTPException(HTTP_404_NOT_FOUND)

    @post(api_paths.START_CRAWLING_PATH)
    def start_crawling(self, request: StartCrawlingRequest,
                       token: str = Depends(AbstractSecuredRoutable.OAUTH2_SCHEME)):
        user_id = self.__get_user_id(token)

        # Making sure that the crawler is being used once per user
        with self.__users_crawling as users_crawling:
            if user_id in users_crawling:
                raise HTTPException(HTTP_423_LOCKED, 'The domain is already being crawled!')
            users_crawling.add(user_id)

        # try-finally block to prevent the user not being removed from the crawling users set
        try:
            # time.sleep(30)
            # return {'result': 'ok'}
            if request.domain is not None:
                # Start crawling a new domain
                parsed_domain = urlparse(request.domain)
                request.domain = f'{parsed_domain.scheme}://{parsed_domain.netloc}/'

                # Adding/overriding crawler state
                self.__database_proxy.put_crawler_state(user_id, request.dict())

                # Adding seed URL
                self.__database_proxy.post_crawler_resource_url(user_id, parsed_domain.path)

            else:
                # New crawling request on the same domain
                if self.__check_if_domain_is_fully_crawled(user_id):
                    self.__log_func(f'[{self.__name}] Invalid crawling attempt:'
                                    f'\n\tClientID: {user_id}'
                                    f'\n\tDomain already finished crawling...')

                    raise HTTPException(HTTP_428_PRECONDITION_REQUIRED, 'The domain is already finished...')

                # Partially updating the crawler state
                self.__database_proxy.patch_crawler_state(user_id, request.dict())

            # Start crawling
            result = self.__crawl_func(user_id)

            if not result['ok']:
                return result
            song = Base64Converter.string_to_bytes(result['song'])
            return Response(content=song, media_type='audio/*')
        # In the end removing the user from the crawling users set (useful if an exception is risen)
        finally:
            with self.__users_crawling as users_crawling:
                users_crawling.remove(user_id)

    def __get_user_id(self, token: str) -> int:
        if not self.__database_proxy.validate_jwt(token):
            raise HTTPException(HTTP_403_FORBIDDEN)
        payload = self._jwt_manager.assert_has_user_type(token, USER)
        return payload['user_id']

    def __check_if_domain_is_fully_crawled(self, user_id: int) -> bool:
        response = self.__database_proxy.get_crawler_resources_urls_count(user_id)
        if response['count'] > 0:
            return False

        response = self.__database_proxy.get_crawler_songs_urls_count(user_id)
        if response['count'] > 0:
            return False

        # TODO: REMOVE OLD CODE
        # self.__database_proxy.patch_crawler_state(user_id, {'finished': True})
        self.__database_proxy.delete_bloom_filter(user_id)

        return True
