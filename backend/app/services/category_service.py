from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import (
    create_category,
    delete_category,
    get_all_categories,
    get_category_by_id,
    get_category_by_name,
)


def list_categories(db: Session) -> list[Category]:
    return get_all_categories(db)


def retrieve_category(
    db: Session,
    category_id: int,
) -> Category:
    category = get_category_by_id(db, category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category


def create_new_category(
    db: Session,
    name: str,
) -> Category:
    cleaned_name = name.strip()

    if len(cleaned_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Category name must contain at least 2 characters",
        )

    existing_category = get_category_by_name(
        db,
        cleaned_name,
    )

    if existing_category is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists",
        )

    return create_category(
        db,
        cleaned_name,
    )


def delete_existing_category(
    db: Session,
    category_id: int,
) -> None:
    category = retrieve_category(
        db,
        category_id,
    )

    delete_category(
        db,
        category,
    )