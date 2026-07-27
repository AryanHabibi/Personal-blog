from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.scalar(
        select(User).where(User.id == user_id)
    )


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:
    return db.scalar(
        select(User).where(User.username == username)
    )


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    return db.scalar(
        select(User).where(User.email == email)
    )


def get_user_by_username_or_email(
    db: Session,
    value: str,
) -> User | None:
    return db.scalar(
        select(User).where(
            or_(
                User.username == value,
                User.email == value,
            )
        )
    )


def create_user(
    db: Session,
    *,
    username: str,
    email: str,
    hashed_password: str,
    role: str = "user",
) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user