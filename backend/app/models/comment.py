from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.blog import Blog
    from app.models.user import User


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            name="fk_comments_user_id_users",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    blog_id: Mapped[int] = mapped_column(
        ForeignKey(
            "blogs.id",
            name="fk_comments_blog_id_blogs",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="comments",
    )

    blog: Mapped["Blog"] = relationship(
        back_populates="comments",
    )