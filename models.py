from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text,
    ForeignKey, CheckConstraint, func, create_engine
)
from sqlalchemy.orm import relationship, declarative_base
# from sqlalchemy.ext.declarative import declarative_base -> 1.3버전 이전까지 import위치, 사용은 무관
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id         = Column(Integer, primary_key=True)
    username   = Column(String(50), unique=True, nullable=False)
    password   = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Restaurant(Base):
    __tablename__ = 'restaurants'
    id         = Column(Integer, primary_key=True)
    name       = Column(String(100), nullable=False)
    category   = Column(String(50))
    address    = Column(String(255))
    latitude   = Column(Float)
    longitude  = Column(Float)
    phone      = Column(String(20))
    hours      = Column(String(100))
    avg_rating = Column(Float, default=0)
    created_at = Column(DateTime, server_default=func.now())

class Review(Base):
    __tablename__ = 'reviews'
    id            = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    user_id       = Column(Integer, ForeignKey('users.id'))
    rating        = Column(Integer)
    comment       = Column(Text)
    created_at    = Column(DateTime, server_default=func.now())
    __table_args__ = (
        CheckConstraint('rating BETWEEN 1 AND 5', name='rating_range_chk'),
    )
    # ORM 편의부분
    # user       = relationship(User, backref='reviews')
    # restaurant = relationship(Restaurant, backref='reviews')
