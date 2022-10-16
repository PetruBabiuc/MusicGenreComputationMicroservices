from threading import Event
from typing import Any, TypeVar, Generic

T = TypeVar('T')


class AwaitableResult(Generic[T]):
    def __init__(self, event: Event, result: T = None):
        self.event = event
        self.result = result
