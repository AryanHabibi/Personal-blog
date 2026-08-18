from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from users.models import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: UserRole
    is_verified: bool
    first_name: str | None
    last_name: str | None
    date_of_birth: date | None
    gender: str | None
    created_at: datetime
