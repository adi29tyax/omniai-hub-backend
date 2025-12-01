from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class ProjectCreate(BaseModel):
    user_id: str
    name: str
    content: Optional[str] = None
    language: str = "python"

class ProjectUpdate(BaseModel):
    content: Optional[str] = None
    language: Optional[str] = None

class ProjectResponse(BaseModel):
    id: UUID
    user_id: str
    name: str
    content: Optional[str]
    language: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
