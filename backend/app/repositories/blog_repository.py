from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.blog import Blog
from app.models.user import User


def get_all_blogs(
    db: Session,
    *,
    offset: int = 0,
    limit: int = 10,
    search: str | None = None,
    category_id: int | None = None,
) -> list[Blog]:
    statement = (
        select(Blog)
        .join(Blog.author)
        .options(
            selectinload(Blog.author),
            selectinload(Blog.category),
        )
        .order_by(Blog.created_at.desc())
    )

    cleaned_search = search.strip() if search else None

    if cleaned_search:
        pattern = f"%{cleaned_search}%"

        statement = statement.where(
            or_(
                Blog.title.ilike(pattern),
                Blog.content.ilike(pattern),
                User.username.ilike(pattern),
            )
        )

    if category_id is not None:
        statement = statement.where(
            Blog.category_id == category_id
        )

    statement = statement.offset(offset).limit(limit)

    return list(db.scalars(statement).unique().all())


def count_blogs(
    db: Session,
    *,
    search: str | None = None,
    category_id: int | None = None,
) -> int:
    statement = (
        select(func.count(Blog.id))
        .select_from(Blog)
        .join(Blog.author)
    )

    cleaned_search = search.strip() if search else None

    if cleaned_search:
        pattern = f"%{cleaned_search}%"

        statement = statement.where(
            or_(
                Blog.title.ilike(pattern),
                Blog.content.ilike(pattern),
                User.username.ilike(pattern),
            )
        )

    if category_id is not None:
        statement = statement.where(
            Blog.category_id == category_id
        )

    return db.scalar(statement) or 0


def get_blog_by_id(
    db: Session,
    blog_id: int,
) -> Blog | None:
    statement = (
        select(Blog)
        .options(
            selectinload(Blog.author),
            selectinload(Blog.category),
        )
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
    category_id: int | None,
) -> Blog:
    blog = Blog(
        title=title,
        content=content,
        image_url=image_url,
        author_id=author_id,
        category_id=category_id,
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
    category_id: int | None,
) -> Blog:
    blog.title = title
    blog.content = content
    blog.image_url = image_url
    blog.category_id = category_id

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return get_blog_by_id(db, blog.id) or blog


def increment_blog_views(
    db: Session,
    blog: Blog,
) -> Blog:
    blog.view_count += 1

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