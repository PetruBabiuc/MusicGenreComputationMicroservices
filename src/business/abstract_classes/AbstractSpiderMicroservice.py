from __future__ import annotations

import collections
import json
import time
from abc import ABCMeta, abstractmethod
from typing import Callable

from pybloomfilter import BloomFilter

from config.constants import LOGGED_URLS
from config.spider import BLOOM_FILTER_CAPACITY, BLOOM_FILTER_ERROR_RATE
from src.AbstractMicroservice import AbstractMicroservice
from src.helpers.abstract_classes.AbstractSpider import AbstractSpider
from src.model.SpiderReturn import SpiderReturn
from src.model.SpiderState import SpiderState


class AbstractSpiderMicroservice(AbstractMicroservice, metaclass=ABCMeta):
    def __init__(self, spider: AbstractSpider,
                 name: str, log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__bloom_filter_file_name = f'{self._name}BloomFilter.raw'
        self.__spider = spider

    def __deserialize_message(self, message: bytes) -> tuple[int, int, int, SpiderState]:
        message = json.loads(message)

        domain = message['domain']
        client_id = message['client_id']
        max_crawled_resources = message['max_crawled_resources']
        max_found_items = message['max_found_items']

        if 'bloom_filter' in message:
            bloom_filter = BloomFilter.from_base64(self.__bloom_filter_file_name, message['bloom_filter'])
        else:
            bloom_filter = BloomFilter(BLOOM_FILTER_CAPACITY, BLOOM_FILTER_ERROR_RATE, self.__bloom_filter_file_name)

        if 'queue' in message:
            queue = message['queue']
        else:
            queue = [domain]
            bloom_filter.add(domain)
        queue = collections.deque(queue)

        return client_id, max_crawled_resources, max_found_items, SpiderState(domain, bloom_filter, queue)

    def _on_received_message(self, message: bytes):
        client_id, max_crawled_resources, max_found_items, state = self.__deserialize_message(message)
        queue = list(state.queue)
        self._log_func(f'[{self._name}] Received state:'
                       f'\n\tClientID: {client_id}'
                       f'\n\tDomain: {state.domain}'
                       f'\n\tMax crawled resources: {max_crawled_resources}'
                       f'\n\tMax found items: {max_found_items}'
                       f'\n\tQueue:'
                       f'\n\t\tCount: {len(queue)}'
                       f'\n\t\tURLs: {queue[:LOGGED_URLS]} ... {queue[-LOGGED_URLS:]}')
        self.__spider.state = state
        self.__spider.max_found_items = max_found_items
        self.__spider.max_crawled_resources = max_crawled_resources
        # TODO: REMOVE DEBUG CODE
        spider_return = self.__spider.crawl()
        # time.sleep(3600)
        # spider_return = SpiderReturn('dom', ['l1', 'l2'], [], 12, '')
        self._log_func(f'[{self._name}] Returned:'
                       f'\n\tClientID: {client_id}'
                       f'\n\tDomain: {spider_return.domain}'
                       f'\n\tQueue:'
                       f'\n\t\tCount: {len(spider_return.queue)}'
                       f'\n\t\tURLs: {spider_return.queue[:LOGGED_URLS]} ... {spider_return.queue[-LOGGED_URLS:]}'
                       f'\n\tURLs to process:'
                       f'\n\t\tCount: {len(spider_return.urls_to_process)}'
                       f'\n\t\tURLs: {spider_return.urls_to_process[:LOGGED_URLS]} ... {spider_return.urls_to_process[-LOGGED_URLS:]}')
        self._send_spider_return(client_id, spider_return)

    @abstractmethod
    def _schedule_domain_request(self, domain: str):
        pass

    @abstractmethod
    def _send_spider_return(self, client_id, spider_return: SpiderReturn) -> None:
        pass
