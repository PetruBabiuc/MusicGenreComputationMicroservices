from sqlalchemy import Column, Integer, String

from src.model.orm.OrmUtils import Base


class SongGenre(Base):
    __tablename__ = 'song_genres'

    song_genre_id = Column(Integer, primary_key=True)
    song_genre_name = Column(String)

    def __init__(self, song_genre_name):
        self.song_genre_name = song_genre_name
