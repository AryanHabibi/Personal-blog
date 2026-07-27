from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    get_user_by_username_or_email,
)
from app.schemas.user import UserCreate


def register_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    return create_user(
        db,
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=hash_password(user_data.password),
        role="user",
    )


def authenticate_user(
    db: Session,
    username_or_email: str,
    password: str,
) -> User:
    user = get_user_by_username_or_email(
        db,
        username_or_email,
    )

    if user is None or not verify_password(
        password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, email, or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def generate_user_token(user: User) -> str:
    return create_access_token(
        subject=str(user.id),
        additional_claims={
            "username": user.username,
            "role": user.role,
        },
    )