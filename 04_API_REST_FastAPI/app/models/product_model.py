# app/models/product_model.py

from sqlalchemy import JSON, Column, Integer, String, Float, Text
from .dec_base import DecBase

class Product(DecBase):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text)
    category = Column(String(50))
    image = Column(String(255))
    rating = Column(JSON)