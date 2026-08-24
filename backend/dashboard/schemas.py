from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SavedBlogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    blog_id: int
    created_at: datetime


class MessageCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1)
    blog_id: int | None = None


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    body: str
    blog_id: int | None
    user_id: int
    created_at: datetime
