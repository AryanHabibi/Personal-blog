from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from blogs.models import Blog
from blogs.schemas import BlogCreate, BlogListOut, BlogOut, BlogUpdate
from categories.models import Category
from core.dependencies import require_role
from database import get_db
from users.models import UserRole

router = APIRouter(prefix="/blogs", tags=["blogs"])


@router.get("", response_model=BlogListOut)
def list_blogs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    q: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
):
    query = db.query(Blog)
    if q:
        like = f"%{q}%"
        query = query.filter((Blog.title.ilike(like)) | (Blog.content.ilike(like)))

    total = query.count()
    items = query.order_by(Blog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return BlogListOut(items=items, total=total, page=page, page_size=page_size)


@router.get("/{blog_id}", response_model=BlogOut)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    return blog


@router.post(
    "",
    response_model=BlogOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def create_blog(payload: BlogCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")

    blog = Blog(title=payload.title, content=payload.content, category_id=payload.category_id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


@router.put(
    "/{blog_id}",
    response_model=BlogOut,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def update_blog(blog_id: int, payload: BlogUpdate, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")

    for field, value in update_data.items():
        setattr(blog, field, value)

    db.commit()
    db.refresh(blog)
    return blog


@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    db.delete(blog)
    db.commit()
