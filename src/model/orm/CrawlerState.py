from sqlalchemy import Column, Integer, String, ForeignKey, Boolean

from src.helpers.ModelUtils import Base


class CrawlerState(Base):
    __tablename__ = 'crawler_state'

    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True)
    desired_genre_id = Column(Integer, ForeignKey('song_genre.song_genre_id'))
    domain = Column(String)
    max_crawled_resources = Column(Integer)
    max_computed_genres = Column(Integer)

    def __init__(self, user_id, desired_genre_id, domain, max_crawled_resources, max_computed_genres, finished=False):
        self.user_id = user_id
        self.desired_genre_id = desired_genre_id
        self.domain = domain
        self.max_crawled_resources = max_crawled_resources
        self.finished = finished
        self.max_computed_genres = max_computed_genres
