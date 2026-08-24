from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from blogs.models import Blog
from core.dependencies import require_role
from dashboard.models import Message, SavedBlog
from dashboard.schemas import MessageCreate, MessageOut, SavedBlogOut
from database import get_db
from users.models import User, UserRole

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.post("/saved-blogs/{blog_id}", response_model=SavedBlogOut, status_code=status.HTTP_201_CREATED)
def save_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.REGULAR)),
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    existing = (
        db.query(SavedBlog)
        .filter(SavedBlog.user_id == current_user.id, SavedBlog.blog_id == blog_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Blog already saved")

    saved = SavedBlog(user_id=current_user.id, blog_id=blog_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.get("/saved-blogs", response_model=list[SavedBlogOut])
def list_saved_blogs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.REGULAR)),
):
    return (
        db.query(SavedBlog)
        .filter(SavedBlog.user_id == current_user.id)
        .order_by(SavedBlog.created_at.desc())
        .all()
    )


@router.delete("/saved-blogs/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.REGULAR)),
):
    saved = (
        db.query(SavedBlog)
        .filter(SavedBlog.user_id == current_user.id, SavedBlog.blog_id == blog_id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved blog not found")

    db.delete(saved)
    db.commit()


@router.post("/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def create_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.REGULAR)),
):
    if payload.blog_id is not None:
        blog = db.query(Blog).filter(Blog.id == payload.blog_id).first()
        if not blog:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Blog not found")

    message = Message(
        user_id=current_user.id,
        blog_id=payload.blog_id,
        subject=payload.subject,
        body=payload.body,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get(
    "/messages",
    response_model=list[MessageOut],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def list_messages(db: Session = Depends(get_db)):
    return db.query(Message).order_by(Message.created_at.desc()).all()
