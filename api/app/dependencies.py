from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.auth import service as auth_service
from app.security import ACCESS_TOKEN_TYPE, decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class CurrentUser:
    def __init__(self, username: str, role: str) -> None:
        self.username = username
        self.role = role
        self.is_admin = role == "admin"


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> CurrentUser:
    if auth_service.is_access_token_revoked(token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token has been revoked")
    try:
        payload = decode_token(token, ACCESS_TOKEN_TYPE)
    except JWTError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Could not validate credentials"
        )
    username = payload.get("sub")
    role = payload.get("role", "regular")
    if not username:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Could not validate credentials"
        )
    return CurrentUser(username=username, role=role)


def require_admin(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin privileges required")
    return user
