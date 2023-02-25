from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.helpers.ModelUtils import Base
from src.model.orm.SongInfo import SongInfo


class Song(Base):
    __tablename__ = 'song'

    song_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    genre_id = Column(Integer, ForeignKey('song_genre.song_genre_id'))
    song_name = Column(String)
    song_info = relationship('SongInfo', uselist=False, backref='parent')

    def __init__(self, user_id, genre_id, song_name):
        self.user_id = user_id
        self.genre_id = genre_id
        self.song_name = song_name

    def to_dict(self) -> dict:
        result = {
            'song_id': self.song_id,
            'user_id': self.user_id,
            'genre_id': self.genre_id,
            'song_name': self.song_name,
        }

        if self.song_info is not None:
            result['song_info'] = {
                'author': self.song_info.author,
                'original_format_id': self.song_info.original_format_id
            }

        return result
