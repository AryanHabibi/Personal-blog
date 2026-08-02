from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.category import Category

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.user import User
    from app.models.comment import Comment


class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "categories.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    author: Mapped["User"] = relationship(
        back_populates="blogs",
    )

    category: Mapped["Category | None"] = relationship(
        back_populates="blogs",
    )
    
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="blog",
        cascade="all, delete-orphan",
    )