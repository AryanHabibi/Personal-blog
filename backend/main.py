from fastapi import FastAPI

app = FastAPI(title="Weblog API")


@app.get("/")
def read_root():
    return {"message": "Weblog API is running"}
