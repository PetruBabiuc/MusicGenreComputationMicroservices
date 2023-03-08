from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from src.helpers.ModelUtils import Base


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    password = Column(String)
    is_active = Column(Boolean)
    user_type_id = Column(Integer, ForeignKey('user_type.user_type_id'))

    def __init__(self, user_name, password, is_active, type_id):
        self.user_name = user_name
        self.password = password
        self.is_active = is_active
        self.type_id = type_id
