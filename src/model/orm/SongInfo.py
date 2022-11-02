from sqlalchemy import Column, Integer, ForeignKey, String

from src.model.orm.OrmUtils import Base


class SongInfo(Base):
    __tablename__ = 'song_info'

    song_id = Column(Integer, ForeignKey('songs.song_id'), primary_key=True)
    author = Column(String)
    original_format_id = Column(Integer, ForeignKey('formats.format_id'))

    def __init__(self, song_id, author, original_format_id):
        self.song_id = song_id
        self.author = author
        self.original_format_id = original_format_id
