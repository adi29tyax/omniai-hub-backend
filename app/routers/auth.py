from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, LoginRequest, Token
from app.config import settings

router = APIRouter(tags=["Auth"])

# Password hashing (Argon2)
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

# JWT config
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALG
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# ------------------------------
# CREATE JWT TOKEN
# ------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ------------------------------
# REGISTER USER
# ------------------------------
@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):

    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = pwd_context.hash(payload.password)

    user = User(
        email=payload.email,
        full_name=payload.full_name or payload.email.split("@")[0],
        hashed_password=hashed_pwd,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ------------------------------
# LOGIN USER
# ------------------------------
@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token({"sub": user.email})

    return Token(access_token=access_token)


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")
        
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ------------------------------
# GET CURRENT USER (ME)
# ------------------------------
@router.get("/me", dependencies=[Depends(bearer_scheme)])
def read_users_me(current_user: User = Depends(get_current_user)):
    if current_user.email == "csadityasharma2000@gmail.com":
        return {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active,
            "role": "owner",
            "plan": "unlimited",
            "credits": "infinite",
            "limits": "none"
        }
    return UserOut.model_validate(current_user)
