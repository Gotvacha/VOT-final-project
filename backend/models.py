from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    products = Column(String(255), nullable=False)
    cook_time_in_m = Column(Integer, nullable=False)
    date_time = Column(DateTime, default=datetime.now, nullable=False)

    def __init__(self, title, products, cook_time_in_m):
        self.title = title
        self.products = products
        self.cook_time_in_m = cook_time_in_m