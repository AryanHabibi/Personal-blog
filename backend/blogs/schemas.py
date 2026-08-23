from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BlogCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    category_id: int


class BlogUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    category_id: int | None = None


class BlogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    category_id: int
    created_at: datetime
    updated_at: datetime


class BlogListOut(BaseModel):
    items: list[BlogOut]
    total: int
    page: int
    page_size: int
