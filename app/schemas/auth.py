from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    full_name: str | None = None
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
