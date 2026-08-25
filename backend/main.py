from fastapi import FastAPI

from blogs.router import router as blogs_router
from categories.router import router as categories_router
from comments.router import router as comments_router
from dashboard.router import router as dashboard_router
from users.router import router as users_router

app = FastAPI(title="Weblog API")
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(blogs_router)
app.include_router(comments_router)
app.include_router(dashboard_router)


@app.get("/")
def read_root():
    return {"message": "Weblog API is running"}
