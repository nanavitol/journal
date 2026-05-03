from sqlalchemy import Column, BigInteger, Date, DateTime, func, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Shift(Base):
    __tablename__ = "shifts"
    
    id = Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    shift_date = Column(Date, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    #status = Column(Enum('planned', 'active', 'completed', name='shift_status'), nullable=False, server_default='planned')
    status = Column(String(20), nullable=False, default='planned')
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('post_id', 'shift_date', name='uq_shift_post_date'),
        {"sqlite_autoincrement": True},
    )
    
    post = relationship("Post", back_populates="shifts")
    assignments = relationship("ShiftAssignment", back_populates="shift", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntry", back_populates="shift", cascade="all, delete-orphan")