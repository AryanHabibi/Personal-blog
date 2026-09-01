from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import storage
from app.blog import service
from app.blog.schema import (
    CommentCreate,
    CommentOut,
    CommentUpdate,
    PaginatedComments,
    PaginatedPosts,
    PostOut,
    ReactionIn,
    ReactionOut,
)
from app.database import get_db
from app.dependencies import CurrentUser, get_current_user, require_admin
from app.storage import ImageError

router = APIRouter(prefix="/blog", tags=["blog"])

# Reads + reactions + commenting: any authenticated user (admin or regular).
AuthUser = Annotated[CurrentUser, Depends(get_current_user)]
# Post writes: admin only.
AdminUser = Annotated[CurrentUser, Depends(require_admin)]
DB = Annotated[Session, Depends(get_db)]

TitleForm = Annotated[str, Form(min_length=1, max_length=200)]
ContentForm = Annotated[str, Form(min_length=1)]
SlugForm = Annotated[str | None, Form(min_length=1, max_length=220)]


# --- posts: reads ---------------------------------------------------------------


@router.get("/posts", response_model=PaginatedPosts)
def list_posts(
    user: AuthUser,
    db: DB,
    page: Annotated[int, Query(ge=1)] = 1,
):
    """Paginated feed, 10 posts per page. Each item carries the caller's
    reaction, like/dislike counts, and an image_url."""
    return service.list_posts(db, page, user.username)


@router.get("/posts/search", response_model=PaginatedPosts)
def search_posts(
    user: AuthUser,
    db: DB,
    q: Annotated[str, Query(min_length=1, description="Matches title or content")],
    page: Annotated[int, Query(ge=1)] = 1,
):
    """Search by title/content. Declared before /posts/{slug} so 'search'
    is not captured as a slug."""
    return service.search_posts(db, q, page, user.username)


@router.get("/posts/{slug}", response_model=PostOut)
def get_post(slug: str, user: AuthUser, db: DB):
    """Single post by its slug, with reaction totals."""
    post = service.get_post_by_slug(db, slug, user.username)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return post


@router.get("/posts/{slug}/image")
def get_post_image(slug: str, user: AuthUser, db: DB):
    """The post's picture (bytes), served with its stored content-type."""
    found = service.get_post_image(db, slug)
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    path, content_type = found
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Image file is missing")
    return FileResponse(path, media_type=content_type)


# --- posts: writes (admin only) --------------------------------------------
# multipart/form-data: text fields via Form(), the picture via File().


@router.post("/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    admin: AdminUser,
    db: DB,
    title: TitleForm,
    content: ContentForm,
    image: Annotated[UploadFile, File(description="JPEG/PNG/WebP, <= 5 MB")],
    slug: SlugForm = None,
):
    """Admin only. A picture is required; slug is derived from the title
    if omitted."""
    try:
        image_filename, image_content_type = storage.save_image(image)
    except ImageError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))
    try:
        return service.create_post(
            db,
            title=title,
            content=content,
            slug=slug,
            image_filename=image_filename,
            image_content_type=image_content_type,
            username=admin.username,
        )
    except ValueError as exc:
        storage.delete_image(image_filename)
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))


@router.put("/posts/{slug}", response_model=PostOut)
def update_post(
    slug: str,
    admin: AdminUser,
    db: DB,
    title: TitleForm,
    content: ContentForm,
    image: Annotated[UploadFile | None, File()] = None,
    new_slug: SlugForm = None,
):
    """Admin only. Full replace of title/content (and slug via `new_slug`).
    Sending `image` swaps the picture; omitting it keeps the current one."""
    image_filename = image_content_type = None
    if image is not None:
        try:
            image_filename, image_content_type = storage.save_image(image)
        except ImageError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))
    try:
        post = service.update_post(
            db,
            slug,
            title=title,
            content=content,
            new_slug=new_slug,
            username=admin.username,
            image_filename=image_filename,
            image_content_type=image_content_type,
        )
    except ValueError as exc:
        storage.delete_image(image_filename)
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))
    if post is None:
        storage.delete_image(image_filename)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return post


@router.delete("/posts/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(slug: str, admin: AdminUser, db: DB):
    """Admin only. Removes the post plus its picture, comments and reactions."""
    if not service.delete_post(db, slug):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")


# --- reactions (both roles) -------------------------------------------------


@router.put("/posts/{slug}/reaction", response_model=ReactionOut)
def set_reaction(slug: str, data: ReactionIn, user: AuthUser, db: DB):
    """Like or dislike a post. Sending the reaction you already hold clears it."""
    result = service.set_reaction(db, slug, user.username, data.value)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return result


@router.delete("/posts/{slug}/reaction", response_model=ReactionOut)
def clear_reaction(slug: str, user: AuthUser, db: DB):
    """Remove the caller's like/dislike from a post."""
    result = service.clear_reaction(db, slug, user.username)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return result


# --- comments -------------------------------------------------------------------


@router.post(
    "/posts/{slug}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(slug: str, data: CommentCreate, user: AuthUser, db: DB):
    """Comment on a post. A `parent_id` makes it a reply - admin only."""
    try:
        comment = service.create_comment(db, slug, user, data)
    except PermissionError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    if comment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return comment


@router.get("/posts/{slug}/comments", response_model=PaginatedComments)
def list_comments(
    slug: str,
    user: AuthUser,
    db: DB,
    page: Annotated[int, Query(ge=1)] = 1,
):
    """Flat list, oldest first, 10 per page. `parent_id` gives the thread shape."""
    result = service.list_comments(db, slug, page)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return result


@router.put("/comments/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int, data: CommentUpdate, user: AuthUser, db: DB
):
    """Edit a comment body. Admin only, and only the admin's own comment."""
    try:
        comment = service.update_comment(db, comment_id, user, data)
    except PermissionError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    if comment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, user: AuthUser, db: DB):
    """Delete a comment (and its replies). Own comment for either role;
    any comment for the admin."""
    try:
        deleted = service.delete_comment(db, comment_id, user)
    except PermissionError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")
