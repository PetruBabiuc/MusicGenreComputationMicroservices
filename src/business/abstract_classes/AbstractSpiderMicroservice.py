from __future__ import annotations

import collections
import json
from abc import ABCMeta, abstractmethod
from typing import Callable

from pybloomfilter import BloomFilter

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

    def __deserialize_message(self, message: bytes) -> tuple[int, SpiderState]:
        message = json.loads(message)

        domain = message['domain']
        client_id = message['client_id']

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

        return client_id, SpiderState(domain, bloom_filter, queue)

    def _on_received_message(self, message: bytes):
        client_id, state = self.__deserialize_message(message)
        self._log_func(f'[{self._name}] Received state:'
                       f'\n\t ClientID: {client_id}'
                       f'\n\t Domain: {state.domain}'
                       f'\n\t Queue: {state.queue}')
        self.__spider.state = state
        spider_return = self.__spider.crawl()
        self._log_func(f'[{self._name}] Returned:'
                       f'\n\t ClientID: {client_id}'
                       f'\n\t Domain: {spider_return.domain}'
                       f'\n\t Queue: {spider_return.queue}'
                       f'\n\t URLs to process: {spider_return.urls_to_process}')
        self._send_spider_return(client_id, spider_return)

    @abstractmethod
    def _schedule_domain_request(self, domain: str):
        pass

    @abstractmethod
    def _send_spider_return(self, client_id, spider_return: SpiderReturn) -> None:
        pass
