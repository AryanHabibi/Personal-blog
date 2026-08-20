from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.email import send_verification_email
from core.security import create_token, decode_token, hash_password, verify_password
from database import get_db
from users.models import User
from users.schemas import Token, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/users", tags=["users"])

VERIFY_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_MINUTES = 60


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    verification_token = create_token(
        {"sub": str(user.id)},
        timedelta(minutes=VERIFY_TOKEN_EXPIRE_MINUTES),
        purpose="email_verification",
    )
    send_verification_email(user.email, verification_token)

    return user


@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_token(token, expected_purpose="email_verification")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_verified = True
    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    access_token = create_token(
        {"sub": str(user.id)},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        purpose="login",
    )
    return Token(access_token=access_token)
