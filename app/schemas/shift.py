from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class ShiftBase(BaseModel):
    post_id: int
    shift_date: date
    start_time: datetime
    end_time: datetime
    status: str = "planned"

class ShiftCreate(ShiftBase):
    pass

class ShiftUpdate(BaseModel):
    post_id: Optional[int] = None
    shift_date: Optional[date] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None

class ShiftResponse(ShiftBase):
    id: int
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ShiftStatusUpdate(BaseModel):
    status: str