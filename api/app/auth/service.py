import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import mailer
from app.auth.model import EmailVerificationToken, RefreshToken, User
from app.auth.schema import MeOut, UserRegister
from app.config import get_settings
from app.security import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

settings = get_settings()

# Access tokens explicitly logged out before their 15-min expiry.
# In-memory is acceptable because an entry only matters for <= 15 min;
# use Redis if you run more than one worker process.
_revoked_access_tokens: set[str] = set()


class EmailNotVerified(Exception):
    """Login attempt by a user whose email is set but not yet confirmed."""


def _aware(dt: datetime) -> datetime:
    """SQLite returns naive datetimes even for DateTime(timezone=True);
    normalise to UTC-aware before comparing."""
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def _issue_verification(db: Session, user: User) -> None:
    """Create a fresh confirmation token for `user` and email the link.
    Caller commits."""
    raw = secrets.token_urlsafe(32)
    db.add(
        EmailVerificationToken(
            user_id=user.id,
            token_hash=_hash_token(raw),
            expires_at=datetime.now(timezone.utc)
            + timedelta(hours=settings.verification_token_ttl_hours),
        )
    )
    link = f"{settings.app_base_url}/auth/verify-email?token={raw}"
    mailer.send_verification_email(user.email, user.first_name, link)


def register_user(db: Session, data: UserRegister) -> User:
    if data.username == settings.admin_username:
        raise ValueError("Username already taken")
    if db.scalar(select(User).where(User.username == data.username)):
        raise ValueError("Username already taken")
    if db.scalar(select(User).where(User.email == data.email)):
        raise ValueError("Email already registered")
    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        gender=data.gender.value if data.gender else None,
        date_of_birth=data.date_of_birth,
        country=data.country,
        phone_number=data.phone_number,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _issue_verification(db, user)
    db.commit()
    return user


def verify_email(db: Session, raw_token: str) -> None:
    row = db.scalar(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == _hash_token(raw_token)
        )
    )
    if row is None or row.used_at is not None:
        raise ValueError("This verification link is invalid or already used")
    if _aware(row.expires_at) <= datetime.now(timezone.utc):
        raise ValueError("This verification link has expired")
    user = db.get(User, row.user_id)
    if user is None:
        raise ValueError("This verification link is invalid or already used")
    user.email_verified = True
    row.used_at = datetime.now(timezone.utc)
    db.commit()


def resend_verification(db: Session, email: str) -> None:
    """Silently issue a new link if that address is registered and unverified.
    Never reveals whether the address exists."""
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user is None or user.email_verified:
        return
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user.id,
        EmailVerificationToken.used_at.is_(None),
    ).update({"used_at": datetime.now(timezone.utc)})
    _issue_verification(db, user)
    db.commit()


def get_me(db: Session, username: str, is_admin: bool) -> MeOut | None:
    """Return the signed-in user's own profile. The admin has no DB row,
    so only username + role are known. Returns None if a regular user's
    row has since disappeared."""
    if is_admin:
        return MeOut(username=username, role="admin")
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        return None
    return MeOut.model_validate(user)  # role defaults to "regular"


def change_password(
    db: Session,
    username: str,
    is_admin: bool,
    current_password: str,
    new_password: str,
) -> None:
    """Change a regular user's own password. Every existing refresh token
    for the account is revoked, so all other sessions are logged out."""
    if is_admin:
        raise ValueError("The admin password is managed in api/app/.env")
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise ValueError("User not found")
    if not verify_password(current_password, user.hashed_password):
        raise ValueError("Current password is incorrect")
    if verify_password(new_password, user.hashed_password):
        raise ValueError("New password must be different from the current one")
    user.hashed_password = hash_password(new_password)
    _revoke_all_for_user(db, user.username)
    db.commit()


def _issue_pair(db: Session, username: str, role: str) -> tuple[str, str, str]:
    """Mint a fresh access + refresh token and record the refresh jti."""
    access_token = create_access_token(subject=username, role=role)
    refresh_token, jti, expires_at = create_refresh_token(subject=username, role=role)
    db.add(RefreshToken(jti=jti, username=username, expires_at=expires_at))
    db.commit()
    return access_token, refresh_token, role


def authenticate(db: Session, username: str, password: str) -> tuple[str, str, str]:
    """Return (access_token, refresh_token, role); raise ValueError on failure."""
    if username == settings.admin_username:
        if password != settings.admin_password:
            raise ValueError("Invalid credentials")
        return _issue_pair(db, username, "admin")

    user = db.scalar(select(User).where(User.username == username))
    if user is None or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")
    if not user.email_verified:
        raise EmailNotVerified()
    return _issue_pair(db, username, "regular")


def rotate_refresh_token(db: Session, refresh_token: str) -> tuple[str, str, str]:
    """Validate a refresh token, single-use it, and issue a new pair."""
    try:
        payload = decode_token(refresh_token, REFRESH_TOKEN_TYPE)
    except JWTError:
        raise ValueError("Invalid refresh token")

    jti = payload.get("jti")
    username = payload.get("sub")
    role = payload.get("role", "regular")
    if not jti or not username:
        raise ValueError("Invalid refresh token")

    record = db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
    if record is None:
        raise ValueError("Invalid refresh token")
    if record.revoked:
        # A revoked token presented again => likely theft. Burn the whole family.
        _revoke_all_for_user(db, username)
        raise ValueError("Refresh token already used")
    if _aware(record.expires_at) <= datetime.now(timezone.utc):
        raise ValueError("Refresh token expired")
    if role != "admin" and not db.scalar(
        select(User).where(User.username == username)
    ):
        raise ValueError("User no longer exists")

    record.revoked = True  # single-use: this refresh token cannot be reused
    db.commit()
    return _issue_pair(db, username, role)


def logout(db: Session, access_token: str, refresh_token: str | None) -> None:
    _revoked_access_tokens.add(access_token)
    if not refresh_token:
        return
    try:
        payload = decode_token(refresh_token, REFRESH_TOKEN_TYPE)
    except JWTError:
        return
    jti = payload.get("jti")
    if not jti:
        return
    record = db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
    if record is not None and not record.revoked:
        record.revoked = True
        db.commit()


def is_access_token_revoked(token: str) -> bool:
    return token in _revoked_access_tokens


def _revoke_all_for_user(db: Session, username: str) -> None:
    db.query(RefreshToken).filter(
        RefreshToken.username == username,
        RefreshToken.revoked.is_(False),
    ).update({"revoked": True})
    db.commit()
