from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from blogs.models import Blog
from comments.models import Comment
from comments.schemas import CommentCreate, CommentOut
from core.dependencies import get_current_user
from database import get_db
from users.models import User, UserRole

router = APIRouter(tags=["comments"])


@router.get("/blogs/{blog_id}/comments", response_model=list[CommentOut])
def list_comments(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    return db.query(Comment).filter(Comment.blog_id == blog_id).order_by(Comment.created_at).all()


@router.post("/blogs/{blog_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    blog_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    comment = Comment(content=payload.content, blog_id=blog_id, user_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    is_owner = comment.user_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment",
        )

    db.delete(comment)
    db.commit()
