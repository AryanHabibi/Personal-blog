from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BlogCreate(BaseModel):
    title: str
    content: str
    image_url: str | None = None


class BlogAuthorResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    image_url: str | None
    created_at: datetime

    author: BlogAuthorResponse

    model_config = ConfigDict(from_attributes=True)