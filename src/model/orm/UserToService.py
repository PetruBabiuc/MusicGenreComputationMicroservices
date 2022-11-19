from sqlalchemy import Column, Integer, ForeignKey, Float

from src.helpers.ModelUtils import Base


class UserToService(Base):
    __tablename__ = 'user_to_service'

    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True)
    service_id = Column(Integer, ForeignKey('service.service_id'), primary_key=True)
    quantity = Column(Float)

    def __init__(self, user_id, service_id, quantity):
        self.user_id = user_id
        self.service_id = service_id
        self.quantity = quantity
