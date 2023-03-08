from abc import ABCMeta, abstractmethod
from typing import Any


class Mp3ValidatorProxyInterface(metaclass=ABCMeta):
    @abstractmethod
    def validate_song(self, request: dict[str, Any]) -> bool:
        pass
