from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.blog import Blog
from app.repositories.blog_repository import (
    count_blogs,
    create_blog,
    delete_blog,
    get_all_blogs,
    get_blog_by_id,
    update_blog,
)

UPLOAD_DIRECTORY = Path("app/uploads")

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
}

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


def list_blogs(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
) -> tuple[list[Blog], int]:
    offset = (page - 1) * page_size

    blogs = get_all_blogs(
        db,
        offset=offset,
        limit=page_size,
        search=search,
    )

    total_items = count_blogs(
        db,
        search=search,
    )

    return blogs, total_items


def retrieve_blog(
    db: Session,
    blog_id: int,
) -> Blog:
    blog = get_blog_by_id(db, blog_id)

    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    return blog


def save_uploaded_image(
    image: UploadFile | None,
) -> str | None:
    if image is None or not image.filename:
        return None

    extension = Path(image.filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format",
        )

    if image.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be an image",
        )

    image.file.seek(0, 2)
    file_size = image.file.tell()
    image.file.seek(0)

    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image must not exceed 5 MB",
        )

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = f"{uuid4().hex}{extension}"
    destination = UPLOAD_DIRECTORY / stored_filename

    try:
        with destination.open("wb") as output_file:
            copyfileobj(image.file, output_file)
    finally:
        image.file.close()

    return f"/uploads/{stored_filename}"


def remove_uploaded_image(
    image_url: str | None,
) -> None:
    if not image_url:
        return

    filename = Path(image_url).name
    image_path = UPLOAD_DIRECTORY / filename

    if image_path.is_file():
        image_path.unlink()


def create_new_blog(
    db: Session,
    *,
    title: str,
    content: str,
    image: UploadFile | None,
    author_id: int,
) -> Blog:
    cleaned_title = title.strip()
    cleaned_content = content.strip()

    if len(cleaned_title) < 3:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title must contain at least 3 characters",
        )

    if len(cleaned_title) > 200:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title must not exceed 200 characters",
        )

    if len(cleaned_content) < 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Content must contain at least 10 characters",
        )

    image_url = save_uploaded_image(image)

    try:
        return create_blog(
            db,
            title=cleaned_title,
            content=cleaned_content,
            image_url=image_url,
            author_id=author_id,
        )
    except Exception:
        remove_uploaded_image(image_url)
        raise


def update_existing_blog(
    db: Session,
    *,
    blog_id: int,
    title: str,
    content: str,
    image: UploadFile | None,
) -> Blog:
    blog = retrieve_blog(db, blog_id)

    cleaned_title = title.strip()
    cleaned_content = content.strip()

    if len(cleaned_title) < 3:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title must contain at least 3 characters",
        )

    if len(cleaned_title) > 200:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Title must not exceed 200 characters",
        )

    if len(cleaned_content) < 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Content must contain at least 10 characters",
        )

    old_image_url = blog.image_url
    new_image_url = old_image_url

    if image is not None and image.filename:
        new_image_url = save_uploaded_image(image)

    try:
        updated_blog = update_blog(
            db,
            blog=blog,
            title=cleaned_title,
            content=cleaned_content,
            image_url=new_image_url,
        )
    except Exception:
        if new_image_url != old_image_url:
            remove_uploaded_image(new_image_url)
        raise

    if new_image_url != old_image_url:
        remove_uploaded_image(old_image_url)

    return updated_blog


def delete_existing_blog(
    db: Session,
    blog_id: int,
) -> None:
    blog = retrieve_blog(db, blog_id)
    image_url = blog.image_url

    delete_blog(db, blog)
    remove_uploaded_image(image_url)