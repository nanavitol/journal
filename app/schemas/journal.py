from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
import uuid

class JournalEntryBase(BaseModel):
    note: str
    entry_type: Optional[str] = None  # routine, incident, handover, other

class JournalEntryCreate(JournalEntryBase):
    pass

class JournalEntryResponse(JournalEntryBase):
    id: int
    shift_id: int
    user_id: str
    full_name_snapshot: str
    created_at: datetime

    @field_validator('user_id', mode='before')
    @classmethod
    def parse_uuid(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True
