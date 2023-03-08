from sqlalchemy import Column, Integer, String

from src.helpers.ModelUtils import Base


class SongFormat(Base):
    __tablename__ = 'song_format'

    format_id = Column(Integer, primary_key=True)
    format_name = Column(String)

    def __init__(self, format_name):
        self.format_name = format_name
