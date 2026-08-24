import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Integer, String, Text

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
    is_verified = Column(Boolean, default=False, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
