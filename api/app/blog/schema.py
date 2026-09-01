from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Post create / replace come in as multipart/form-data (title, content, slug,
# image file), so their inputs are declared with Form()/File() in the router,
# not as Pydantic models here.


class _Reactions(BaseModel):
    likes: int = 0
    dislikes: int = 0
    my_reaction: Literal["like", "dislike"] | None = None


class PostOut(_Reactions):
    """Full post - single-post view and write results."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    content: str
    image_url: str
    created_at: datetime


class PostSummary(_Reactions):
    """Lightweight post - list/search items (no body)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    image_url: str
    created_at: datetime


class PaginatedPosts(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    items: list[PostSummary]


# --- reactions -----------------------------------------------------------------


class ReactionIn(BaseModel):
    value: Literal["like", "dislike"]


class ReactionOut(_Reactions):
    pass


# --- comments ----------------------------------------------------------------


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    parent_id: int | None
    author_username: str
    author_role: str
    body: str
    created_at: datetime
    updated_at: datetime | None


class PaginatedComments(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    items: list[CommentOut]
