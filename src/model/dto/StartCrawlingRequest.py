from typing import Union

from pydantic import BaseModel


class StartCrawlingRequest(BaseModel):
    max_crawled_resources: int
    max_computed_genres: int
    desired_genre_id: int
    domain: Union[str, None] = None
