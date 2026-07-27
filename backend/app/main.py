from fastapi import FastAPI

app = FastAPI(
    title="Blog Management API",
    description="Simple Blog API with JWT Authentication",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Blog Management API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }