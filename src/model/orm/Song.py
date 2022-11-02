from sqlalchemy import Column, Integer, String, ForeignKey

from src.model.orm.OrmUtils import Base


class Song(Base):
    __tablename__ = 'songs'

    song_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    genre_id = Column(Integer, ForeignKey('song_genres.song_genre_id'))
    song_name = Column(String)

    def __init__(self, user_id, genre_id, song_name):
        self.user_id = user_id
        self.genre_id = genre_id
        self.song_name = song_name
