from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_admin
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
)
from app.services.category_service import (
    create_new_category,
    delete_existing_category,
    list_categories,
    retrieve_category,
)


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get(
    "",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all categories",
)
def get_categories(
    db: Annotated[Session, Depends(get_db)],
):
    return list_categories(db)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get one category",
)
def get_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return retrieve_category(
        db,
        category_id,
    )


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
)
def create_category(
    category_data: CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
):
    return create_new_category(
        db,
        category_data.name,
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
)
def delete_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
) -> Response:
    delete_existing_category(
        db,
        category_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )