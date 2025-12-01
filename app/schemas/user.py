from pydantic import BaseModel, EmailStr
from typing import Optional


# ---------------------------
# USER CREATE
# ---------------------------
class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str


# ---------------------------
# USER OUTPUT (RESPONSE)
# ---------------------------
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True  # replaces orm_mode=True


# ---------------------------
# LOGIN REQUEST
# ---------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------------------------
# TOKEN RESPONSE
# ---------------------------
class Token(BaseModel):
    access_token: str
