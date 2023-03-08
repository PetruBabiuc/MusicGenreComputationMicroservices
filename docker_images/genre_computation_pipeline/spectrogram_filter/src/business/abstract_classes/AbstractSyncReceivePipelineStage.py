from abc import abstractmethod

from src.business.abstract_classes.AbstractPipelineStage import AbstractPipelineStage


class AbstractSyncReceivePipelineStage(AbstractPipelineStage):
    @abstractmethod
    def _receive_message(self) -> bytes:
        pass

    def run(self) -> None:
        while True:
            message = self._receive_message()
            message = self._process_message(message)
            self._send_message(message)
