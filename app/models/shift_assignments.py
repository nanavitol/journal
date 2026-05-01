from sqlalchemy import Column, BigInteger, Boolean, DateTime, func, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class ShiftAssignment(Base):
    __tablename__ = "shift_assignments"
    
    id = Column(BigInteger, primary_key=True)
    shift_id = Column(BigInteger, ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_leader = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('shift_id', 'user_id', name='uq_shift_user'),
        Index('ix_shift_leader_unique', 'shift_id', unique=True, postgresql_where=Column('is_leader')),
        {"sqlite_autoincrement": True},
    )
    
    shift = relationship("Shift", back_populates="assignments")
    user = relationship("User", back_populates="shift_assignments")