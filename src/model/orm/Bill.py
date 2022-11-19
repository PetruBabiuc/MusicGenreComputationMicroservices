from sqlalchemy import Column, Integer, ForeignKey, Float, Date, Boolean

from src.helpers.ModelUtils import Base


class Bill(Base):
    __tablename__ = 'bill'

    bill_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    price = Column(Float)
    deadline = Column(Date)
    is_paid = Column(Boolean)

    def __init__(self, user_id, price, deadline, is_paid):
        self.user_id = user_id
        self.price = price
        self.deadline = deadline
        self.is_paid = is_paid
