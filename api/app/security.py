import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _encode(claims: dict, expire: datetime) -> str:
    payload = {**claims, "iat": datetime.now(timezone.utc), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return _encode({"sub": subject, "role": role, "type": ACCESS_TOKEN_TYPE}, expire)


def create_refresh_token(subject: str, role: str) -> tuple[str, str, datetime]:
    """Return (token, jti, expires_at). The jti is tracked in the DB so the
    token can be revoked (logout) and rotated (single-use on /auth/refresh)."""
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    token = _encode(
        {"sub": subject, "role": role, "type": REFRESH_TOKEN_TYPE, "jti": jti}, expire
    )
    return token, jti, expire


def decode_token(token: str, expected_type: str) -> dict:
    """Decode a JWT and enforce that its ``type`` claim matches expected_type,
    so an access token can never be used where a refresh token is required
    (or vice versa). Raises jose.JWTError on any problem."""
    payload = jwt.decode(
        token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )
    if payload.get("type") != expected_type:
        raise JWTError(f"Expected a {expected_type} token")
    return payload
