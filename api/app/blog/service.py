import re
from datetime import datetime, timezone
from math import ceil
from pathlib import Path

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app import storage
from app.blog.model import Comment, Post, PostReaction
from app.blog.schema import CommentCreate, CommentUpdate
from app.dependencies import CurrentUser

PAGE_SIZE = 10

_slug_re = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    slug = _slug_re.sub("-", value.strip().lower()).strip("-")
    return slug or "post"


# --- reaction aggregates ---------------------------------------------------


def _reaction_summary(
    db: Session, post_ids: list[int], username: str
) -> dict[int, dict]:
    base = {pid: {"likes": 0, "dislikes": 0, "my_reaction": None} for pid in post_ids}
    if not post_ids:
        return base
    counts = db.execute(
        select(PostReaction.post_id, PostReaction.value, func.count())
        .where(PostReaction.post_id.in_(post_ids))
        .group_by(PostReaction.post_id, PostReaction.value)
    ).all()
    for pid, value, count in counts:
        if value == "like":
            base[pid]["likes"] = count
        elif value == "dislike":
            base[pid]["dislikes"] = count
    mine = db.execute(
        select(PostReaction.post_id, PostReaction.value).where(
            PostReaction.post_id.in_(post_ids),
            PostReaction.username == username,
        )
    ).all()
    for pid, value in mine:
        base[pid]["my_reaction"] = value
    return base


def _post_payload(post: Post, rx: dict) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "content": post.content,
        "image_url": f"/blog/posts/{post.slug}/image",
        "created_at": post.created_at,
        "likes": rx["likes"],
        "dislikes": rx["dislikes"],
        "my_reaction": rx["my_reaction"],
    }


# --- post reads ----------------------------------------------------------------


def _paginate(db: Session, stmt: Select, page: int, username: str) -> dict:
    page = max(page, 1)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(Post.created_at.desc())
        .offset((page - 1) * PAGE_SIZE)
        .limit(PAGE_SIZE)
    ).all()
    rx = _reaction_summary(db, [p.id for p in rows], username)
    return {
        "page": page,
        "page_size": PAGE_SIZE,
        "total": total,
        "total_pages": ceil(total / PAGE_SIZE) if total else 0,
        "items": [_post_payload(p, rx[p.id]) for p in rows],
    }


def list_posts(db: Session, page: int, username: str) -> dict:
    return _paginate(db, select(Post), page, username)


def search_posts(db: Session, q: str, page: int, username: str) -> dict:
    pattern = f"%{q}%"
    stmt = select(Post).where(
        or_(Post.title.ilike(pattern), Post.content.ilike(pattern))
    )
    return _paginate(db, stmt, page, username)


def get_post_by_slug(db: Session, slug: str, username: str) -> dict | None:
    post = db.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        return None
    rx = _reaction_summary(db, [post.id], username)
    return _post_payload(post, rx[post.id])


def get_post_image(db: Session, slug: str) -> tuple[Path, str] | None:
    """(path on disk, content-type) for a post's image, or None if no post."""
    post = db.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        return None
    return storage.image_path(post.image_filename), post.image_content_type


# --- post writes (admin only, enforced in the router) ------------------------
#
# The router saves/validates the uploaded file and passes the stored filename
# in. Removing a file (on replace or delete) is done here, where the row's
# lifecycle is owned.


def create_post(
    db: Session,
    *,
    title: str,
    content: str,
    slug: str | None,
    image_filename: str,
    image_content_type: str,
    username: str,
) -> dict:
    final_slug = slugify(slug or title)
    if db.scalar(select(Post).where(Post.slug == final_slug)):
        raise ValueError("A post with this slug already exists")
    post = Post(
        title=title,
        content=content,
        slug=final_slug,
        image_filename=image_filename,
        image_content_type=image_content_type,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    rx = _reaction_summary(db, [post.id], username)
    return _post_payload(post, rx[post.id])


def update_post(
    db: Session,
    slug: str,
    *,
    title: str,
    content: str,
    new_slug: str | None,
    username: str,
    image_filename: str | None = None,
    image_content_type: str | None = None,
) -> dict | None:
    post = db.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        return None
    target_slug = slugify(new_slug) if new_slug else post.slug
    if target_slug != post.slug and db.scalar(
        select(Post).where(Post.slug == target_slug)
    ):
        raise ValueError("A post with this slug already exists")
    post.title = title
    post.content = content
    post.slug = target_slug
    if image_filename is not None:
        storage.delete_image(post.image_filename)
        post.image_filename = image_filename
        post.image_content_type = image_content_type
    db.commit()
    db.refresh(post)
    rx = _reaction_summary(db, [post.id], username)
    return _post_payload(post, rx[post.id])


def delete_post(db: Session, slug: str) -> bool:
    post = db.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        return False
    storage.delete_image(post.image_filename)
    db.query(Comment).filter(Comment.post_id == post.id).delete()
    db.query(PostReaction).filter(PostReaction.post_id == post.id).delete()
    db.delete(post)
    db.commit()
    return True


# --- reactions (both roles) -------------------------------------------------


def set_reaction(
    db: Session, slug: str, username: str, value: str
) -> dict | None:
    post = db.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        return None
    existing = db.scalar(
        select(PostReaction).where(
            PostReaction.post_id == post.id, PostReaction.username == username
        )
    )
    if existing is None:
        db.add(PostReaction(post_id=post.id, username=username, value=value))
    elif existing.value == value:
        db.delete(existing)  # clicking the same reaction again clears it
    else:
        existing.value = value
    db.commit()
    return _reaction_summary(db, [post.id], username)[post.id]


def clear_reaction(db: Session, slug: str, username: str) -> dict | None:
    post = db.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        return None
    existing = db.scalar(
        select(PostReaction).where(
            PostReaction.post_id == post.id, PostReaction.username == username
        )
    )
    if existing is not None:
        db.delete(existing)
        db.commit()
    return _reaction_summary(db, [post.id], username)[post.id]


# --- comments --------------------------------------------------------------
#
# Permission rules (literal spec):
#   create top-level ....... both roles
#   reply (parent_id set) .. admin only
#   edit ................... admin only, own comment only
#   delete ................ own comment (either role), or any comment (admin)


def create_comment(
    db: Session, slug: str, current: CurrentUser, data: CommentCreate
) -> Comment | None:
    post = db.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        return None
    if data.parent_id is not None:
        if not current.is_admin:
            raise PermissionError("Only an admin can reply to a comment")
        parent = db.get(Comment, data.parent_id)
        if parent is None or parent.post_id != post.id:
            raise ValueError("Parent comment not found on this post")
    comment = Comment(
        post_id=post.id,
        parent_id=data.parent_id,
        author_username=current.username,
        author_role=current.role,
        body=data.body,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments(db: Session, slug: str, page: int) -> dict | None:
    post = db.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        return None
    page = max(page, 1)
    stmt = select(Comment).where(Comment.post_id == post.id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(Comment.created_at.asc())
        .offset((page - 1) * PAGE_SIZE)
        .limit(PAGE_SIZE)
    ).all()
    return {
        "page": page,
        "page_size": PAGE_SIZE,
        "total": total,
        "total_pages": ceil(total / PAGE_SIZE) if total else 0,
        "items": rows,
    }


def update_comment(
    db: Session, comment_id: int, current: CurrentUser, data: CommentUpdate
) -> Comment | None:
    comment = db.get(Comment, comment_id)
    if comment is None:
        return None
    if not (current.is_admin and comment.author_username == current.username):
        raise PermissionError("You cannot edit this comment")
    comment.body = data.body
    comment.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment_id: int, current: CurrentUser) -> bool:
    comment = db.get(Comment, comment_id)
    if comment is None:
        return False
    is_owner = comment.author_username == current.username
    if not (is_owner or current.is_admin):
        raise PermissionError("You cannot delete this comment")
    db.query(Comment).filter(Comment.parent_id == comment.id).delete()
    db.delete(comment)
    db.commit()
    return True
