from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=1000,
    )


class CommentUpdate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=1000,
    )


class CommentUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    created_at: datetime
    user_id: int
    blog_id: int
    user: CommentUserResponse