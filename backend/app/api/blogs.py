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
from app.schemas.blog import BlogListResponse, BlogResponse
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
    response_model=BlogListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get and search blogs",
)
def get_blogs(
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    page: Annotated[
        int,
        Query(
            ge=1,
            description="Page number",
        ),
    ] = 1,
    page_size: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Number of blogs per page",
        ),
    ] = 10,
    search: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=100,
            description=(
                "Search blog titles, content, "
                "and author usernames"
            ),
        ),
    ] = None,
    category_id: Annotated[
        int | None,
        Query(
            ge=1,
            description="Filter blogs by category ID",
        ),
    ] = None,
) -> BlogListResponse:
    """
    Return a paginated list of blogs.

    The optional search value checks:

    - Blog titles
    - Blog content
    - Author usernames

    Authentication is not required.
    """

    blogs, total_items = list_blogs(
        db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
    )

    return BlogListResponse.build(
        items=[
            BlogResponse.model_validate(blog)
            for blog in blogs
        ],
        page=page,
        page_size=page_size,
        total_items=total_items,
    )


@router.get(
    "/{blog_id}",
    response_model=BlogResponse,
    status_code=status.HTTP_200_OK,
    summary="Get one blog",
)
def get_blog(
    blog_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> BlogResponse:
    """
    Return one blog by its database ID.

    Authentication is not required.
    """

    return retrieve_blog(
        db,
        blog_id,
        increase_views=True,
    )


@router.post(
    "",
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a blog",
)
def create_blog(
    title: Annotated[
        str,
        Form(
            min_length=3,
            max_length=200,
        ),
    ],
    content: Annotated[
        str,
        Form(
            min_length=10,
        ),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
    image: Annotated[
        UploadFile | None,
        File(),
    ] = None,
    category_id: Annotated[
        int | None,
        Form(),
    ] = None,
) -> BlogResponse:
    """
    Create a new blog using multipart form data.

    Only an administrator can access this endpoint.
    """

    return create_new_blog(
        db,
        title=title,
        content=content,
        image=image,
        author_id=current_admin.id,
        category_id=category_id,
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
        Form(
            min_length=3,
            max_length=200,
        ),
    ],
    content: Annotated[
        str,
        Form(
            min_length=10,
        ),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
    image: Annotated[
        UploadFile | None,
        File(),
    ] = None,
    category_id: Annotated[
        int | None,
        Form(),
    ] = None,
        
) -> BlogResponse:
    """
    Update an existing blog.

    Uploading a new image replaces the existing image.

    Leaving the image field empty keeps the current image.

    Only an administrator can access this endpoint.
    """

    return update_existing_blog(
        db,
        blog_id=blog_id,
        title=title,
        content=content,
        image=image,
        category_id=category_id,
    )


@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a blog",
)
def delete_blog(
    blog_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_admin: Annotated[
        User,
        Depends(get_current_admin),
    ],
) -> Response:
    """
    Delete a blog and its associated uploaded image.

    Only an administrator can access this endpoint.
    """

    delete_existing_blog(
        db,
        blog_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )