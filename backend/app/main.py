from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.database.database import Base, engine

# Import the models before create_all() so SQLAlchemy knows about them.
from app.models.blog import Blog  # noqa: F401
from app.models.user import User  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Run application startup and shutdown tasks.

    During startup, create any database tables that do not exist yet.
    """

    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="Blog Management API",
    description="Simple Blog API with JWT authentication and role-based access.",
    version="1.0.0",
    lifespan=lifespan,
)


# Register API routers.
app.include_router(auth_router)


@app.get(
    "/",
    tags=["System"],
    summary="API root",
)
def root() -> dict[str, str]:
    """
    Return a simple message confirming that the API is running.
    """

    return {
        "message": "Welcome to Blog Management API",
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
)
def health() -> dict[str, str]:
    """
    Return the current application health status.
    """

    return {
        "status": "healthy",
    }