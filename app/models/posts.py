from sqlalchemy import Column, BigInteger, Text, Time, Numeric, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(BigInteger, primary_key=True)
    city_id = Column(BigInteger, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)
    default_start_time = Column(Time)
    default_end_time = Column(Time)
    price_per_shift = Column(Numeric(10, 2), nullable=False, default=0)
    max_workers = Column(Integer, nullable=False, default=5)
    photo_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    city = relationship("City", back_populates="posts")
    shifts = relationship("Shift", back_populates="post", cascade="all, delete-orphan")