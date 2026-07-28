from datetime import datetime
from math import ceil

from pydantic import BaseModel, ConfigDict, Field


class BlogCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
    )
    content: str = Field(min_length=10)
    image_url: str | None = None


class BlogAuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class BlogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    image_url: str | None
    created_at: datetime
    updated_at: datetime
    author_id: int
    author: BlogAuthorResponse


class BlogListResponse(BaseModel):
    items: list[BlogResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int

    @classmethod
    def build(
        cls,
        *,
        items: list[BlogResponse],
        page: int,
        page_size: int,
        total_items: int,
    ) -> "BlogListResponse":
        total_pages = (
            ceil(total_items / page_size)
            if total_items > 0
            else 0
        )

        return cls(
            items=items,
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        )