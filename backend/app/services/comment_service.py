from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.user import User
from app.repositories.blog_repository import get_blog_by_id
from app.repositories.comment_repository import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    get_comments_by_blog,
    update_comment,
)


def list_blog_comments(
    db: Session,
    blog_id: int,
) -> list[Comment]:
    blog = get_blog_by_id(db, blog_id)

    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    return get_comments_by_blog(
        db,
        blog_id,
    )


def create_new_comment(
    db: Session,
    *,
    blog_id: int,
    content: str,
    current_user: User,
) -> Comment:
    blog = get_blog_by_id(db, blog_id)

    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    cleaned_content = content.strip()

    if not cleaned_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Comment cannot be empty",
        )

    return create_comment(
        db,
        content=cleaned_content,
        blog_id=blog_id,
        user_id=current_user.id,
    )


def update_existing_comment(
    db: Session,
    *,
    comment_id: int,
    content: str,
    current_user: User,
) -> Comment:
    comment = get_comment_by_id(
        db,
        comment_id,
    )

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    is_owner = comment.user_id == current_user.id
    is_admin = current_user.role == "admin"

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot edit this comment",
        )

    cleaned_content = content.strip()

    if not cleaned_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Comment cannot be empty",
        )

    return update_comment(
        db,
        comment=comment,
        content=cleaned_content,
    )


def delete_existing_comment(
    db: Session,
    *,
    comment_id: int,
    current_user: User,
) -> None:
    comment = get_comment_by_id(
        db,
        comment_id,
    )

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    is_owner = comment.user_id == current_user.id
    is_admin = current_user.role == "admin"

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete this comment",
        )

    delete_comment(
        db,
        comment,
    )