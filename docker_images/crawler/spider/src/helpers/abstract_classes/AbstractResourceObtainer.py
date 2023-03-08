from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')


class AbstractResourceObtainer(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def obtain_resource(self, url: str) -> T:
        pass
