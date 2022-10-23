from typing import Callable

from src.AbstractMicroservice import AbstractMicroservice
from src.helpers.SynchronizedDict import SynchronizedDict


class CrawlerRepository(AbstractMicroservice):
    def __init__(self, name: str = 'CrawlerRepository', log_func: Callable[[str], None] = print):
        super().__init__(name, log_func)
        self.__db: SynchronizedDict[int, dict[str, dict]] = SynchronizedDict()
        self.__db[1] = {
            'spider': {
                'allowed_domains': ['']
            }
        }

    def run(self) -> None:
        pass
