from fastapi import FastAPI
from app.api.upload import router as upload_router

from app.routes.download import (
    router as download_router
)

app = FastAPI(
    title="AI Data Cleaner",
    version="1.0.0"
)

app.include_router(upload_router)

@app.get("/")
def home():
    return {
        "message": "AI Data Cleaner Backend Running"
    }


app.include_router(
    download_router
)