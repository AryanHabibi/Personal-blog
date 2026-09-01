from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.schema import (
    LogoutRequest,
    MessageOut,
    RefreshRequest,
    ResendVerification,
    TokenPair,
    UserOut,
    UserRegister,
)
from app.database import get_db
from app.dependencies import CurrentUser, get_current_user, oauth2_scheme

router = APIRouter(prefix="/auth", tags=["auth"])

DB = Annotated[Session, Depends(get_db)]


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: DB):
    """Regular-user sign-up. A confirmation link is emailed; the account cannot
    log in until it is verified."""
    try:
        return service.register_user(db, data)
    except ValueError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))


@router.post("/login", response_model=TokenPair)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DB):
    """Login for both regular users and the admin. Returns a 15-min access
    token and a 7-day refresh token."""
    try:
        access_token, refresh_token, role = service.authenticate(
            db, form.username, form.password
        )
    except service.EmailNotVerified:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Verify your email address before logging in",
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc))
    return TokenPair(access_token=access_token, refresh_token=refresh_token, role=role)


@router.get("/verify-email", response_model=MessageOut)
def verify_email(token: str, db: DB):
    """Target of the emailed link. Marks the address confirmed."""
    try:
        service.verify_email(db, token)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    return MessageOut(detail="Email verified. You can now log in.")


@router.post("/verify-email/resend", response_model=MessageOut)
def resend_verification(data: ResendVerification, db: DB):
    """Request a fresh confirmation link. Always returns 200 so it cannot be
    used to probe which addresses are registered."""
    service.resend_verification(db, data.email)
    return MessageOut(
        detail="If that address is registered and unverified, a new link has been sent."
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, db: DB):
    """Exchange a valid refresh token for a new pair. The old refresh token is
    single-use and is revoked here (rotation)."""
    try:
        access_token, refresh_token, role = service.rotate_refresh_token(
            db, data.refresh_token
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc))
    return TokenPair(access_token=access_token, refresh_token=refresh_token, role=role)


@router.post("/logout", response_model=MessageOut)
def logout(
    data: LogoutRequest,
    token: Annotated[str, Depends(oauth2_scheme)],
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    db: DB,
):
    """Revoke the current access token and the supplied refresh token."""
    service.logout(db, token, data.refresh_token)
    return MessageOut(detail="Logged out")
