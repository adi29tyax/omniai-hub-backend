from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# ✅ Use Argon2 instead of bcrypt (secure + Windows friendly)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


@router.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check duplicate email
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # ✅ No more 72-byte limitation
    hashed_pwd = pwd_context.hash(payload.password)

    user = models.User(
        email=payload.email,
        full_name=payload.full_name or payload.email.split("@")[0],
        hashed_password=hashed_pwd,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # ✅ Temporary token placeholder
    token = "fake-jwt-token-for-now"

    return schemas.Token(access_token=token)
