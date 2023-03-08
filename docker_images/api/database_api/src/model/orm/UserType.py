from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


class UserType(declarative_base()):
    __tablename__ = 'user_types'

    user_type_id = Column(Integer, primary_key=True)
    user_type_name = Column(String)

    def __init__(self, user_type_name):
        self.user_type_name = user_type_name
