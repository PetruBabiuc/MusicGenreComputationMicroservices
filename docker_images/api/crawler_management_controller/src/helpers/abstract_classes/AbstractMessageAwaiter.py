from abc import ABCMeta, abstractmethod
from threading import Event
from typing import TypeVar, Generic

from src.helpers.SynchronizedDict import SynchronizedDict
from src.model.AwaitableResult import AwaitableResult

K = TypeVar('K')  # Key's type of the synchronized dict
V = TypeVar('V')  # Value's type of the synchronized dict


class AbstractMessageAwaiter(Generic[K, V], metaclass=ABCMeta):
    def __init__(self):
        self.__sync_dict: SynchronizedDict[K, AwaitableResult[V]] = SynchronizedDict()

    def put_awaitable(self, key: K) -> None:
        with self.__sync_dict as sync_dict:
            sync_dict[key] = AwaitableResult(Event())

    def await_result(self, key: K) -> V:
        with self.__sync_dict as sync_dict:
            awaitable_result = sync_dict[key]
        awaitable_result.event.wait()
        with self.__sync_dict as sync_dict:
            try:
                del sync_dict[key]
            except KeyError:  # Another thread deleted the entry...
                pass
        return awaitable_result.result

    def _put_result_and_notify(self, key: K, result: V) -> None:
        with self.__sync_dict as sync_dict:
            awaitable_result = sync_dict[key]
            awaitable_result.result = result
            awaitable_result.event.set()

    def contains_key(self, key: K) -> bool:
        return key in self.__sync_dict

    def awaited_messages_count(self) -> int:
        with self.__sync_dict as sync_dict:
            return len(sync_dict)

    @abstractmethod
    def start_receiving_responses(self) -> None:
        pass
