from abc import abstractmethod

from src.business.abstract_classes.AbstractPipelineStage import AbstractPipelineStage


class AbstractAsyncReceivePipelineStage(AbstractPipelineStage):
    @abstractmethod
    def _receive_message(self) -> None:
        pass

    def _on_received_message(self, message: bytes) -> None:
        message = self._process_message(message)
        self._send_message(message)

    def run(self) -> None:
        while True:
            self._receive_message()
