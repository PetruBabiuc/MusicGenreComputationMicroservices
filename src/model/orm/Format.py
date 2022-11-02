from sqlalchemy import Column, Integer, String

from src.model.orm.OrmUtils import Base


class SongGenre(Base):
    __tablename__ = 'formats'

    format_id = Column(Integer, primary_key=True)
    format_name = Column(String)

    def __init__(self, format_name):
        self.format_name = format_name
