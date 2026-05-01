from sqlalchemy import Column, Text, Boolean, DateTime, func, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    login = Column(Text, unique=True, nullable=False)
    full_name = Column(Text, nullable=False)
    city_id = Column(BigInteger, ForeignKey("cities.id", ondelete="SET NULL"))
    role = Column(Text, nullable=False)
    password_changed = Column(Boolean, default=False)
    photo_url = Column(Text)
    rank = Column(Text)
    phone = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    city = relationship("City", back_populates="users")
    shift_assignments = relationship("ShiftAssignment", back_populates="user")
    journal_entries = relationship("JournalEntry", back_populates="user")