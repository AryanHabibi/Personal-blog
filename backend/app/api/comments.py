from typing import Annotated

from fastapi import APIRouter, Depends, Form, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)
from app.services.comment_service import (
    create_new_comment,
    delete_existing_comment,
    list_blog_comments,
    update_existing_comment,
)

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


@router.get(
    "/blog/{blog_id}",
    response_model=list[CommentResponse],
)
def get_comments(
    blog_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    return list_blog_comments(
        db=db,
        blog_id=blog_id,
    )


@router.post(
    "/blog/{blog_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    blog_id: int,
    data: Annotated[CommentCreate, Form()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return create_new_comment(
        db=db,
        blog_id=blog_id,
        content=data.content,
        current_user=current_user,
    )


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_id: int,
    data: Annotated[CommentCreate, Form()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return update_existing_comment(
        db=db,
        comment_id=comment_id,
        content=data.content,
        current_user=current_user,
    )


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    delete_existing_comment(
        db=db,
        comment_id=comment_id,
        current_user=current_user,
    )