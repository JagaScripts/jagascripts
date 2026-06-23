from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class UserBase(BaseModel):
    email: str = Field(..., description="User email")
    username: str = Field(..., min_length=3, max_length=50, description="Username")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="User password")
    name: Dict[str, str] = Field(..., description="First and last name")
    address: Dict[str, Any] = Field(..., description="User address")
    phone: str = Field(..., description="Phone number")

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, description="User email")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    password: Optional[str] = Field(None, min_length=6, description="User password")
    name: Optional[Dict[str, str]] = Field(None, description="First and last name")
    address: Optional[Dict[str, Any]] = Field(None, description="User address")
    phone: Optional[str] = Field(None, description="Phone number")

class UserResponse(UserBase):
    id: int = Field(..., description="User ID")
    name: Dict[str, str] = Field(..., description="First and last name")
    address: Dict[str, Any] = Field(..., description="User address")
    phone: str = Field(..., description="Phone number")

    class Config:
        from_attributes = True  # Para ORM compatibility