from abc import ABCMeta, abstractmethod
from typing import Callable


class AsyncMessageConsumerInterface(metaclass=ABCMeta):
    @abstractmethod
    def start_receiving_messages(self) -> None:
        pass

    @abstractmethod
    def set_message_callback(self, callback: Callable[[bytes], None]) -> None:
        pass
