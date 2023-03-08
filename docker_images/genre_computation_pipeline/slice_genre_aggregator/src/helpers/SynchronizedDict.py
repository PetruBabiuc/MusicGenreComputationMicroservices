from threading import Lock
from typing import TypeVar

K = TypeVar('K')
V = TypeVar('V')


class SynchronizedDict(dict[K, V]):
    def __init__(self):
        super().__init__()
        self.__lock = Lock()

    def __enter__(self) -> dict[K, V]:
        self.__lock.acquire()
        # print('Acquired!')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # print('Released!')
        self.__lock.release()
