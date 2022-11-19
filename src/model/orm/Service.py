from sqlalchemy import Column, Integer, String, Float

from src.helpers.ModelUtils import Base


class Service(Base):
    __tablename__ = 'service'

    service_id = Column(Integer, primary_key=True)
    service_name = Column(String)
    price = Column(Float)

    def __init__(self, service_name, price):
        self.service_name = service_name
        self.price = price
