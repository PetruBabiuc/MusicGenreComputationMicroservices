from threading import Event
from typing import Any


class AwaitableResult:
    def __init__(self, event: Event, result: dict[str, Any] = None):
        self.event = event
        self.result = result
