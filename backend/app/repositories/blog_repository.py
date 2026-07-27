from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.blog import Blog


def get_all_blogs(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 20,
) -> list[Blog]:
    statement = (
        select(Blog)
        .options(selectinload(Blog.author))
        .order_by(Blog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def get_blog_by_id(
    db: Session,
    blog_id: int,
) -> Blog | None:
    statement = (
        select(Blog)
        .options(selectinload(Blog.author))
        .where(Blog.id == blog_id)
    )

    return db.scalar(statement)


def create_blog(
    db: Session,
    *,
    title: str,
    content: str,
    image_url: str | None,
    author_id: int,
) -> Blog:
    blog = Blog(
        title=title,
        content=content,
        image_url=image_url,
        author_id=author_id,
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return get_blog_by_id(db, blog.id) or blog


def update_blog(
    db: Session,
    *,
    blog: Blog,
    title: str,
    content: str,
    image_url: str | None,
) -> Blog:
    blog.title = title
    blog.content = content
    blog.image_url = image_url

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return get_blog_by_id(db, blog.id) or blog


def delete_blog(
    db: Session,
    blog: Blog,
) -> None:
    db.delete(blog)
    db.commit()