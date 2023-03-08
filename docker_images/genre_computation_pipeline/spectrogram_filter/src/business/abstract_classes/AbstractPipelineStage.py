from abc import abstractmethod
from src.AbstractMicroservice import AbstractMicroservice


class AbstractPipelineStage(AbstractMicroservice):
    @abstractmethod
    def _process_message(self, message: bytes) -> bytes:
        pass

    @abstractmethod
    def _send_message(self, message: bytes) -> None:
        pass
