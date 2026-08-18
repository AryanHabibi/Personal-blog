import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String

from database import Base


class UserRole(str, enum.Enum):
    REGULAR = "regular"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.REGULAR, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
