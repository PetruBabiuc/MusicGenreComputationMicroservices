from sqlalchemy import Column, Integer, ForeignKey, Float

from src.model.orm.OrmUtils import Base


class UserToService(Base):
    __tablename__ = 'users_to_services'

    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    service_id = Column(Integer, ForeignKey('services.service_id'), primary_key=True)
    quantity = Column(Float)

    def __init__(self, user_id, service_id, quantity):
        self.user_id = user_id
        self.service_id = service_id
        self.quantity = quantity
