from collections import deque
from dataclasses import dataclass

from pybloomfilter import BloomFilter


@dataclass
class SpiderState:
    domain: str
    bloom_filter: BloomFilter
    queue: deque[str]
