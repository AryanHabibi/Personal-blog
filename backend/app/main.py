from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.blogs import router as blogs_router
from app.core.config import settings
from app.database.database import SessionLocal
from app.services.seed_service import seed_admin_user
from app.api.categories import router as categories_router
from app.api.comments import router as comments_router

UPLOAD_DIRECTORY = Path("app/uploads")
UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Seed the default administrator account at startup.

    Database schema changes are managed by Alembic.
    """

    db = SessionLocal()

    try:
        seed_admin_user(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title="Blog Management API",
    description="Simple Blog API with JWT authentication and role-based access.",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIRECTORY),
    name="uploads",
)


app.include_router(auth_router)
app.include_router(blogs_router)
app.include_router(categories_router)
app.include_router(comments_router)

@app.get(
    "/",
    tags=["System"],
    summary="API root",
)
def root() -> dict[str, str]:
    return {
        "message": "Welcome to Blog Management API",
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
)
def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }