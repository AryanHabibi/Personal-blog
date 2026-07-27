from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.blogs import router as blogs_router
from app.database.database import Base, SessionLocal, engine
from app.models.blog import Blog  # noqa: F401
from app.models.user import User  # noqa: F401
from app.services.seed_service import seed_admin_user


UPLOAD_DIRECTORY = Path("app/uploads")
UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

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
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
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