from dataclasses import dataclass


@dataclass
class SpiderReturn:
    domain: str
    queue: list[str]
    urls_to_process: list[str]
    resources_crawled: int
    bloom_filter: str
