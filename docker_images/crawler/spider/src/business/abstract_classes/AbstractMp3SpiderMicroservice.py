from abc import ABCMeta
from typing import Callable

from config.spider import MAX_FOUND_ITEMS, MAX_CRAWLED_RESOURCES
from src.business.abstract_classes.AbstractSpiderMicroservice import AbstractSpiderMicroservice
from src.helpers.Mp3Spider import Mp3Spider


class AbstractMp3SpiderMicroservice(AbstractSpiderMicroservice, metaclass=ABCMeta):
    def __init__(self, name: str,
                 log_func: Callable[[str], None] = print):
        spider = Mp3Spider(max_found_items=MAX_FOUND_ITEMS, max_crawled_resources=MAX_CRAWLED_RESOURCES,
                           domain_request_scheduler=self._schedule_domain_request)
        super().__init__(spider, name, log_func)
