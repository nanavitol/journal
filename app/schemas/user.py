from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: str
    login: str
    full_name: str
    city_id: Optional[int] = None
    role: str = Field(..., pattern="^(admin|worker)$")
    rank: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    city_id: Optional[int] = None
    rank: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    password_changed: bool
    photo_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True