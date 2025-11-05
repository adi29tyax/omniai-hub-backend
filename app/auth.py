from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pwd_context.verify(p, hashed)

def _create_token(sub: str, secret: str, expires_minutes: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALG)

def create_access_token(sub: str) -> str:
    return _create_token(sub, settings.JWT_SECRET_KEY, settings.ACCESS_TOKEN_EXPIRE_MINUTES)

def create_refresh_token(sub: str) -> str:
    return _create_token(sub, settings.JWT_REFRESH_SECRET_KEY, settings.REFRESH_TOKEN_EXPIRE_MINUTES)

def decode_access(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALG])
    except JWTError:
        return None
