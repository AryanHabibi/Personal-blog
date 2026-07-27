from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
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
    summary="Register a regular user",
)
def register(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Create a new regular user account.

    The role is assigned as `user` by the authentication service.
    A client cannot register itself as an administrator.
    """

    return register_user(
        db=db,
        user_data=user_data,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in and receive a JWT token",
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """
    Authenticate using a username or email and password.

    Although Swagger labels the first field as `username`, this application
    accepts either a username or an email address in that field.
    """

    user = authenticate_user(
        db=db,
        username_or_email=form_data.username,
        password=form_data.password,
    )

    access_token = generate_user_token(user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the current user",
)
def get_my_profile(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:
    """
    Return the account information for the currently authenticated user.

    A valid Bearer JWT token is required.
    """

    return current_user