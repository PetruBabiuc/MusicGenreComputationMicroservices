from time import sleep
from typing import Callable

from src.helpers.abstract_classes.AbstractSpider import AbstractSpider
from src.helpers.resource_processors.HtmlProcessor import HtmlProcessor
from src.helpers.resource_processors.Mp3Processor import Mp3Processor
from src.model.SpiderState import SpiderState


class Mp3Spider(AbstractSpider):
    def __init__(self, state: SpiderState = None, /,
                 max_found_items=1, max_crawled_resources=0, bloom_filter_name: str = 'bloom_filter.raw',
                 bloom_filter_capacity: int = 10_000_000, bloom_filter_error_rate: float = 0.1,
                 domain_request_scheduler: Callable[[str], None] = lambda _: sleep(0.25)):
        processors = [HtmlProcessor(), Mp3Processor()]
        super().__init__(processors, state, max_found_items, max_crawled_resources, bloom_filter_name,
                         bloom_filter_capacity, bloom_filter_error_rate, domain_request_scheduler)
