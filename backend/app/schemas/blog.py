from datetime import datetime

from pydantic import BaseModel, ConfigDict


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