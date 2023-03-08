from abc import ABCMeta, abstractmethod


class MessageProducerInterface(metaclass=ABCMeta):
    @abstractmethod
    def send_message(self, message: bytes) -> None:
        pass
