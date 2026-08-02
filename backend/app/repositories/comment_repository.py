from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.comment import Comment


def get_comments_by_blog(
    db: Session,
    blog_id: int,
) -> list[Comment]:
    statement = (
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.blog_id == blog_id)
        .order_by(Comment.created_at.desc())
    )

    return list(db.scalars(statement).all())


def get_comment_by_id(
    db: Session,
    comment_id: int,
) -> Comment | None:
    statement = (
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.id == comment_id)
    )

    return db.scalar(statement)


def create_comment(
    db: Session,
    *,
    content: str,
    blog_id: int,
    user_id: int,
) -> Comment:
    comment = Comment(
        content=content,
        blog_id=blog_id,
        user_id=user_id,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return get_comment_by_id(db, comment.id) or comment


def update_comment(
    db: Session,
    *,
    comment: Comment,
    content: str,
) -> Comment:
    comment.content = content

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return get_comment_by_id(db, comment.id) or comment


def delete_comment(
    db: Session,
    comment: Comment,
) -> None:
    db.delete(comment)
    db.commit()