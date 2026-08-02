from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


def get_all_categories(db: Session) -> list[Category]:
    statement = select(Category).order_by(Category.name.asc())
    return list(db.scalars(statement).all())


def get_category_by_id(
    db: Session,
    category_id: int,
) -> Category | None:
    return db.scalar(
        select(Category).where(Category.id == category_id)
    )


def get_category_by_name(
    db: Session,
    name: str,
) -> Category | None:
    return db.scalar(
        select(Category).where(Category.name == name)
    )


def create_category(
    db: Session,
    name: str,
) -> Category:
    category = Category(name=name)

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def delete_category(
    db: Session,
    category: Category,
) -> None:
    db.delete(category)
    db.commit()