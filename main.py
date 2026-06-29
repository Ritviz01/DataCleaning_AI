from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.routes.download import router as download_router
from app.routes.analysis import router as analysis_router
from app.routes.dashboard import router as dashboard_router
from app.routes.pipeline import router as pipeline_router
from app.api.copilot import router as copilot_router
from app.services.settings import load_local_env
from app.db.session import engine, Base
import app.models  # Registers models with Base.metadata

from fastapi.middleware.cors import CORSMiddleware

load_local_env()
app = FastAPI(title="AI Data Cleaner", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(upload_router)
app.include_router(download_router)
app.include_router(analysis_router)
app.include_router(dashboard_router)
app.include_router(pipeline_router)
app.include_router(copilot_router)



@app.get("/")
def home():
    return {
        "message": "DataClean AI is running",
        "docs": "/docs",
        "workflow": "POST /datasets/analyze to inspect a dataset, then POST /datasets/clean to export a cleaned copy.",
    }

