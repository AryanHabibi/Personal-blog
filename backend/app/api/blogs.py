from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_admin
from app.models.user import User
from app.schemas.blog import BlogResponse
from app.services.blog_service import (
    create_new_blog,
    delete_existing_blog,
    list_blogs,
    retrieve_blog,
    update_existing_blog,
)


router = APIRouter(
    prefix="/blogs",
    tags=["Blogs"],
)


@router.get(
    "",
    response_model=list[BlogResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all blogs",
)
def get_blogs(
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """
    Return published blogs.

    Authentication is not required.
    """

    return list_blogs(
        db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{blog_id}",
    response_model=BlogResponse,
    status_code=status.HTTP_200_OK,
    summary="Get one blog",
)
def get_blog(
    blog_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Return one blog by its database ID.

    Authentication is not required.
    """

    return retrieve_blog(db, blog_id)


@router.post(
    "",
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a blog",
)
def create_blog(
    title: Annotated[
        str,
        Form(min_length=3, max_length=200),
    ],
    content: Annotated[
        str,
        Form(min_length=10),
    ],
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
    image: Annotated[
        UploadFile | None,
        File(),
    ] = None,
):
    """
    Create a new blog using multipart form data.

    Only administrators can access this endpoint.
    """

    return create_new_blog(
        db,
        title=title,
        content=content,
        image=image,
        author_id=current_admin.id,
    )


@router.put(
    "/{blog_id}",
    response_model=BlogResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a blog",
)
def update_blog(
    blog_id: int,
    title: Annotated[
        str,
        Form(min_length=3, max_length=200),
    ],
    content: Annotated[
        str,
        Form(min_length=10),
    ],
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
    image: Annotated[
        UploadFile | None,
        File(),
    ] = None,
):
    """
    Update a blog.

    Uploading a new image replaces the existing image.
    Leaving the image field empty keeps the current image.
    """

    return update_existing_blog(
        db,
        blog_id=blog_id,
        title=title,
        content=content,
        image=image,
    )


@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a blog",
)
def delete_blog(
    blog_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
) -> Response:
    """
    Delete a blog and its associated uploaded image.

    Only administrators can access this endpoint.
    """

    delete_existing_blog(db, blog_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )