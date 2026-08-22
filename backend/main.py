from fastapi import FastAPI

from categories.models import Category  # noqa: F401  (import registers the table with Base.metadata)
from categories.router import router as categories_router
from database import Base, engine
from users.models import User  # noqa: F401  (import registers the table with Base.metadata)
from users.router import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Weblog API")
app.include_router(users_router)
app.include_router(categories_router)


@app.get("/")
def read_root():
    return {"message": "Weblog API is running"}
