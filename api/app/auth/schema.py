import re
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

_PHONE_RE = re.compile(r"\+?[0-9][0-9 ()\-]{5,19}")


class Gender(str, Enum):
    male = "male"
    female = "female"
    non_binary = "non_binary"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class UserRegister(BaseModel):
    # --- required ---
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr

    # --- optional profile ---
    gender: Gender | None = None
    date_of_birth: date | None = None
    country: str | None = Field(
        default=None, description="ISO 3166-1 alpha-2 country code, e.g. US"
    )
    phone_number: str | None = Field(default=None, max_length=20)

    @field_validator("first_name", "last_name")
    @classmethod
    def _tidy_name(cls, v: str) -> str:
        v = " ".join(v.split())  # trim + collapse inner whitespace, keep casing
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("email")
    @classmethod
    def _normalise_email(cls, v: str) -> str:
        return v.lower()

    @field_validator("country")
    @classmethod
    def _country_code(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip().upper()
        if len(v) != 2 or not v.isalpha():
            raise ValueError("country must be a 2-letter ISO code, e.g. US")
        return v

    @field_validator("phone_number")
    @classmethod
    def _tidy_phone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not _PHONE_RE.fullmatch(v):
            raise ValueError(
                "phone_number: 6-20 chars of digits, spaces, (), - and an "
                "optional leading +"
            )
        return v

    @field_validator("date_of_birth")
    @classmethod
    def _dob_in_past(cls, v: date | None) -> date | None:
        if v is None:
            return None
        today = date.today()
        if v >= today:
            raise ValueError("date_of_birth must be in the past")
        if v.year < today.year - 120:
            raise ValueError("date_of_birth is unrealistically far in the past")
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    email_verified: bool
    gender: Gender | None
    date_of_birth: date | None
    country: str | None
    phone_number: str | None
    created_at: datetime


class ResendVerification(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.lower()


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class MessageOut(BaseModel):
    detail: str
