from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_username,
)


def seed_admin_user(db: Session) -> None:
    """
    Create the default administrator account if it does not exist.

    This function is safe to call every time the application starts.
    """

    existing_username = get_user_by_username(
        db,
        settings.ADMIN_USERNAME,
    )

    existing_email = get_user_by_email(
        db,
        settings.ADMIN_EMAIL,
    )

    if existing_username or existing_email:
        return

    create_user(
        db,
        username=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        hashed_password=hash_password(
            settings.ADMIN_PASSWORD,
        ),
        role="admin",
    )