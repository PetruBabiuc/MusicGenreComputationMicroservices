from sqlalchemy import Column, Integer, String
from src.helpers.ModelUtils import Base


class UserType(Base):
    __tablename__ = 'user_type'

    user_type_id = Column(Integer, primary_key=True)
    user_type_name = Column(String)

    def __init__(self, user_type_name):
        self.user_type_name = user_type_name
