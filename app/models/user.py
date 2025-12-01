from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    org_id = Column(Integer, default=1)
    role = Column(String, default="free") # Enum: 'owner','admin','free','pro','ultra'

    # Relationship to Project
    projects = relationship("Project", back_populates="creator")
    usage = relationship("UserUsage", back_populates="user", uselist=False)
