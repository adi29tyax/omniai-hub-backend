from pydantic import BaseModel, EmailStr
from typing import Optional


# =======================
# User Schemas
# =======================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =======================
# Project Schemas
# =======================

class ProjectBase(BaseModel):
    name: str


class ProjectCreate(ProjectBase):
    description: Optional[str] = None


class ProjectOut(ProjectBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
