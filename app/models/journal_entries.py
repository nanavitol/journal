from sqlalchemy import Column, BigInteger, Text, DateTime, func, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(BigInteger, primary_key=True)
    shift_id = Column(BigInteger, ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    full_name_snapshot = Column(Text, nullable=False)
    note = Column(Text, nullable=False)
    #entry_type = Column(Enum('routine', 'incident', 'handover', 'other', name='entry_type'), nullable=False)
    entry_type = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    shift = relationship("Shift", back_populates="journal_entries")
    user = relationship("User", back_populates="journal_entries")