import uuid
from sqlalchemy import Column, String, Text, DateTime, func, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class IDEProjectFile(Base):
    __tablename__ = "ide_project_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("ide_projects.id"), nullable=False)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    is_folder = Column(Boolean, default=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
