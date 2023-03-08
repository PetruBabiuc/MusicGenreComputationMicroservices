from abc import ABCMeta, abstractmethod
from typing import Callable


class AbstractMicroservice(metaclass=ABCMeta):
    def __init__(self, name: str, log_func: Callable[[str], None] = print):
        self._log_func = log_func
        self._name = name

    @abstractmethod
    def run(self) -> None:
        pass
