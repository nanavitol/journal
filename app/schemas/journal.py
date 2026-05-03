from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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

    class Config:
        from_attributes = True