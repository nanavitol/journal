from pydantic import BaseModel
from typing import Optional
from datetime import time

class PostBase(BaseModel):
    name: str
    description: Optional[str] = None
    default_start_time: Optional[time] = None
    default_end_time: Optional[time] = None
    price_per_shift: float = 0
    max_workers: int = 5
    photo_url: Optional[str] = None

class PostCreate(PostBase):
    city_id: int

class PostUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_start_time: Optional[time] = None
    default_end_time: Optional[time] = None
    price_per_shift: Optional[float] = None
    max_workers: Optional[int] = None
    photo_url: Optional[str] = None

class PostResponse(PostBase):
    id: int
    city_id: int

    class Config:
        from_attributes = True