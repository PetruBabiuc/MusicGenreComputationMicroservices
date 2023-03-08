from abc import ABCMeta, abstractmethod


class SyncMessageConsumerInterface(metaclass=ABCMeta):
    @abstractmethod
    def receive_message(self) -> bytes:
        pass
