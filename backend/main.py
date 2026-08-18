from fastapi import FastAPI

from database import Base, engine
from users.models import User  # noqa: F401  (import registers the table with Base.metadata)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Weblog API")


@app.get("/")
def read_root():
    return {"message": "Weblog API is running"}
