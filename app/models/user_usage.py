from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class UserUsage(Base):
    __tablename__ = "user_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    episodes_generated = Column(Integer, default=0)
    ai_calls = Column(Integer, default=0)
    storage_used_mb = Column(Float, default=0.0)
    keyframes = Column(Integer, default=0)
    animations = Column(Integer, default=0)
    timeline_builds = Column(Integer, default=0)
    last_reset = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="usage")
