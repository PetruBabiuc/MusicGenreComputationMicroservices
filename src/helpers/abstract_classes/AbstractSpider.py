from abc import ABCMeta
from time import sleep
from typing import Iterable, Callable
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests

from config.constants import LOGGED_URLS
from src.helpers.abstract_classes.AbstractMimeContentProcessor import AbstractMimeContentProcessor
from src.model.SpiderReturn import SpiderReturn
from src.model.SpiderState import SpiderState
from tests.presentation.tests import time_it


class AbstractSpider(metaclass=ABCMeta):
    def __init__(self, processors: Iterable[AbstractMimeContentProcessor],
                 state: SpiderState = None, /, max_found_items=0, max_crawled_resources=0,
                 domain_request_scheduler: Callable[[str], None] = lambda _: sleep(0.25)):
        self.__resource_processors = processors
        self.__request_validator = RobotFileParser()
        self.state = state

        self.max_crawled_resources = max_crawled_resources
        self.max_found_items = max_found_items
        self.domain_request_scheduler = domain_request_scheduler

    @property
    def max_crawled_resources(self) -> int:
        return self.__max_crawled_resource

    @max_crawled_resources.setter
    def max_crawled_resources(self, value: int) -> None:
        self.__max_crawled_resource = value

    @property
    def max_found_items(self) -> int:
        return self.__max_found_items

    @max_found_items.setter
    def max_found_items(self, value: int) -> None:
        self.__max_found_items = value

    @property
    def domain_request_scheduler(self) -> Callable[[str], None]:
        return self.__domain_request_scheduler

    @domain_request_scheduler.setter
    def domain_request_scheduler(self, value: Callable[[str], None]) -> None:
        self.__domain_request_scheduler = value

    @property
    def state(self) -> SpiderState:
        return self.__state

    @state.setter
    def state(self, value: SpiderState) -> None:
        self.__state = value
        if value is not None:
            self.__request_validator.set_url(urljoin(value.domain, '/robots.txt'))
            self.__request_validator.read()

    @domain_request_scheduler.setter
    def domain_request_scheduler(self, value: Callable[[], None]) -> None:
        self.__domain_request_scheduler = value

    @staticmethod
    def __get_resource_types(url: str) -> list[str]:
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers['Content-Type']
        types = content_type.split(';')
        return [it.strip().casefold() for it in types]

    @time_it
    def crawl(self) -> SpiderReturn:
        resources_crawled = 0
        state = self.__state
        items_to_process = []

        while (self.__max_crawled_resource == 0 or resources_crawled < self.__max_crawled_resource) and \
                (self.__max_found_items == 0 or len(items_to_process) < self.__max_found_items) and \
                len(state.queue) > 0:

            url_to_process = state.queue.pop()
            if not self.__request_validator.can_fetch('*', url_to_process):
                print(f'Not allowed to be crawled (robots.txt): {url_to_process}')
                continue
            resources_crawled += 1

            self.__domain_request_scheduler(state.domain)
            resource_types = self.__get_resource_types(urljoin(state.domain, url_to_process))

            resource_accepted = False
            for resource_processor in self.__resource_processors:
                if resource_processor.accept_any_of_types(resource_types):
                    resource_accepted = True
                    self.__domain_request_scheduler(state.domain)
                    found_urls, url_should_be_processed = resource_processor.process_resource(url_to_process,
                                                                                              state.domain)
                    found_urls = list(filter(lambda it: it not in state.bloom_filter, found_urls))
                    state.queue.extendleft(found_urls)
                    state.bloom_filter.update(found_urls)
                    if url_should_be_processed:
                        items_to_process.append(url_to_process)

                    print(f'{resource_processor.__class__.__name__}\tprocessing {url_to_process} =>'
                          f'\n\tWill be sent to UrlProcessors: {url_should_be_processed}'
                          f'\n\tFound URLs:'
                          f'\n\t\tCount: {len(found_urls)}'
                          f'\n\t\tURLs: {found_urls[:LOGGED_URLS]} ... {found_urls[-LOGGED_URLS:]}')

            if not resource_accepted:
                print(f'There was no MimeContentProcessor that accepted the resource {url_to_process}.')

        # Returning the bloom filter either the crawl seems to be completed or not
        base64_bloom_filter = state.bloom_filter.to_base64().decode()

        return SpiderReturn(state.domain, list(state.queue),
                            items_to_process, resources_crawled, base64_bloom_filter)
