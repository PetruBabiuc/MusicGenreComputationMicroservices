from sqlalchemy import Column, Integer, String, ForeignKey

from src.model.orm.OrmUtils import Base


class SongUrl(Base):
    __tablename__ = 'song_urls'

    song_url_id = Column(Integer, primary_key=True)
    song_url = Column(String)
    user_id = Column(Integer, ForeignKey('crawler_states.user_id'))
    genre_id = Column(Integer, ForeignKey('song_genres.song_genre_id'))

    def __init__(self, song_url, user_id, genre_id):
        self.song_url = song_url
        self.user_id = user_id
        self.genre_id = genre_id
