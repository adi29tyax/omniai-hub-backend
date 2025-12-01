from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class FileCreate(BaseModel):
    project_id: str
    path: str
    name: str
    is_folder: bool = False
    content: Optional[str] = None

class FileUpdate(BaseModel):
    content: Optional[str] = None
    name: Optional[str] = None

class FileResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    path: str
    is_folder: bool
    content: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FileTreeItem(BaseModel):
    id: UUID
    name: str
    path: str
    is_folder: bool
    children: Optional[List['FileTreeItem']] = None

    class Config:
        from_attributes = True
