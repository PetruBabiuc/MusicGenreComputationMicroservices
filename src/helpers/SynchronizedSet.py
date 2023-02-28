from threading import Lock
from typing import TypeVar

T = TypeVar('T')


class SynchronizedSet(set[T]):
    def __init__(self):
        super().__init__()
        self.__lock = Lock()

    def __enter__(self) -> set[T]:
        self.__lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__lock.release()
