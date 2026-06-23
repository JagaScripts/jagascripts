# app/models/cart_model.py

from sqlalchemy import Column, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .dec_base import DecBase

class CartItem(DecBase):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    userId = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime)
    products = Column(JSON)
    
    user = relationship("User", back_populates="carts")