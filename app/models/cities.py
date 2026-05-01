from sqlalchemy import Column, BigInteger, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class City(Base):
    __tablename__ = "cities"
    
    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    posts = relationship("Post", back_populates="city", cascade="all, delete-orphan")
    users = relationship("User", back_populates="city", cascade="all, delete-orphan")