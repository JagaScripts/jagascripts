from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ProductBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Product title")
    price: float = Field(..., gt=0, description="Product price")
    description: Optional[str] = Field(None, description="Product description")
    category: str = Field(..., min_length=1, max_length=50, description="Product category")
    image: str = Field(..., description="Product image URL")

class ProductCreate(ProductBase):
    rating: Dict[str, Any] = Field(..., description="Product rating")

class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Product title")
    price: Optional[float] = Field(None, gt=0, description="Product price")
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, min_length=1, max_length=50, description="Product category")
    image: Optional[str] = Field(None, description="Product image URL")
    rating: Optional[Dict[str, Any]] = Field(None, description="Product rating")

class ProductResponse(ProductBase):
    id: int = Field(..., description="Product ID")
    rating: Dict[str, Any] = Field(..., description="Product rating")

    class Config:
        from_attributes = True