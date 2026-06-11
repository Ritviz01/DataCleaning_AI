from fastapi import APIRouter, UploadFile, File
import os
import shutil

from app.services.file_detector import detect_file_type
from app.services.dataset_reader import read_dataset
from app.services.metadata_service import generate_metadata
from app.services.schema_engine import infer_schema
from app.services.profiling_service import profile_dataset


router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_type = detect_file_type(file.filename)

    # Read dataset
    df = read_dataset(file_path, file_type)

    # Generate metadata
    metadata = generate_metadata(df)

    schema = infer_schema(df)

    profile = profile_dataset(df)

    return {
        "filename": file.filename,
        "file_type": file_type,
        "metadata": metadata,
        "schema": schema,
        "profile": profile
    }