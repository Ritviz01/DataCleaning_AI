from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.routes.download import router as download_router
from app.routes.analysis import router as analysis_router
from app.routes.dashboard import router as dashboard_router
from app.services.settings import load_local_env

load_local_env()
app = FastAPI(title="AI Data Cleaner", version="1.0.0")
app.include_router(upload_router)
app.include_router(download_router)
app.include_router(analysis_router)
app.include_router(dashboard_router)


@app.get("/")
def home():
    return {
        "message": "DataClean AI is running",
        "docs": "/docs",
        "workflow": "POST /datasets/analyze to inspect a dataset, then POST /datasets/clean to export a cleaned copy.",
    }
