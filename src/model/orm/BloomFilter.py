from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT

from src.helpers.ModelUtils import Base


class BloomFilter(Base):
    __tablename__ = 'bloom_filter'

    user_id = Column(Integer, ForeignKey('crawler_state.user_id'), primary_key=True)
    value = Column(LONGTEXT)

    def __init__(self, user_id, value):
        self.user_id = user_id
        self.value = value
