from fastapi import FastAPI

from blogs.models import Blog  # noqa: F401  (import registers the table with Base.metadata)
from blogs.router import router as blogs_router
from categories.models import Category  # noqa: F401  (import registers the table with Base.metadata)
from categories.router import router as categories_router
from comments.models import Comment  # noqa: F401  (import registers the table with Base.metadata)
from comments.router import router as comments_router
from dashboard.models import Message, SavedBlog  # noqa: F401  (import registers the tables with Base.metadata)
from dashboard.router import router as dashboard_router
from database import Base, engine
from users.models import User  # noqa: F401  (import registers the table with Base.metadata)
from users.router import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Weblog API")
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(blogs_router)
app.include_router(comments_router)
app.include_router(dashboard_router)


@app.get("/")
def read_root():
    return {"message": "Weblog API is running"}
