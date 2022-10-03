from abc import ABCMeta, abstractmethod
from typing import Callable


class AsyncMessageConsumerInterface(metaclass=ABCMeta):
    @abstractmethod
    def receive_message(self) -> None:
        pass

    @abstractmethod
    def set_message_callback(self, callback: Callable[[bytes], None]) -> None:
        pass
