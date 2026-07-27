from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import (
    get_current_admin,
    get_current_user,
)
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import (
    authenticate_user,
    generate_user_token,
    register_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Register a new user.
    """

    return register_user(
        db=db,
        user_data=user_data,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    """
    Login using username and password.
    """

    user = authenticate_user(
        db=db,
        username_or_email=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password.",
        )

    token = generate_user_token(user)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    """
    Return currently authenticated user.
    """

    return current_user


@router.get(
    "/admin-check",
    response_model=UserResponse,
)
def admin_check(
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
):
    """
    Test endpoint to verify admin authorization.
    """

    return current_admin