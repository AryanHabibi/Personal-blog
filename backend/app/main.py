from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.database import Base, engine
from app.models import Blog, User  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Blog Management API",
    description="Simple Blog API with JWT Authentication",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Blog Management API",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }