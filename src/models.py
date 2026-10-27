# ORM-модель
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    sku = Column(String)
    rating = Column(Integer)
    text = Column(String)
    source = Column(String)  # 'csv', 'ozon', 'wildberries'
