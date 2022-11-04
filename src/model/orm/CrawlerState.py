from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT

from src.model.orm.OrmUtils import Base


class CrawlerState(Base):
    __tablename__ = 'crawler_states'

    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    desired_genre_id = Column(Integer, ForeignKey('song_genres.song_genre_id'))
    domain = Column(String)
    bloom_filter = Column(LONGTEXT)
    max_crawled_resources = Column(Integer)
    max_computed_genres = Column(Integer)
    finished = Column(Boolean)

    def __init__(self, user_id, desired_genre_id, domain, max_crawled_resources, max_computed_genres,
                 bloom_filter=None, finished=False):
        self.user_id = user_id
        self.desired_genre_id = desired_genre_id
        self.domain = domain
        self.bloom_filter = bloom_filter
        self.max_crawled_resources = max_crawled_resources
        self.finished = finished
        self.max_computed_genres = max_computed_genres
