from fastapi import FastAPI

# Import models so their tables are registered on Base.metadata (used by Alembic).
from app.auth import model as _auth_model  # noqa: F401
from app.auth.router import router as auth_router
from app.blog import model as _blog_model  # noqa: F401
from app.blog.router import router as blog_router

app = FastAPI(title="weblog API")

app.include_router(auth_router)
app.include_router(blog_router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "healthy"}
