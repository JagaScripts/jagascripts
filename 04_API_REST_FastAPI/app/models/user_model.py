# app/models/user_model.py

from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from .dec_base import DecBase

class User(DecBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(JSON) 
    address = Column(JSON)  
    phone = Column(String)

    carts = relationship("CartItem", back_populates="user")