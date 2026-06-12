from duckdb import df
from fastapi import APIRouter, UploadFile, File
import os
import shutil

from app.services.file_detector import detect_file_type
from app.services.dataset_reader import read_dataset
from app.services.metadata_service import generate_metadata
from app.services.schema_engine import infer_schema
from app.services.profiling_service import profile_dataset
from app.services.quality_score import calculate_quality_score
# Issue detector import
from app.services.issue_detector import detect_issues
# Column cleaner import
from app.services.column_cleaner import clean_column_names
# Recommendation Engine
from app.services.recommendation_engine import generate_recommendations
# Type inference engine
from app.services.type_inference_engine import infer_better_types



router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        # Detect uploaded file type
    file_type = detect_file_type(file.filename)

    # Read dataset
    df = read_dataset(file_path, file_type)

    # Clean column names
    df = clean_column_names(df)

    # Generate metadata
    metadata = generate_metadata(df)

    # Generate schema
    schema = infer_schema(df)

    # Generate profile
    profile = profile_dataset(df)

    # Detect issues
    issues = detect_issues(df)

    # Calculate quality score
    quality = calculate_quality_score(issues)

    # Generate cleaning recommendations
    recommendations = generate_recommendations(
        issues,
        schema
    )

    # Infer better data types
    type_suggestions = infer_better_types(df)

    return {
    "filename": file.filename,
    "file_type": file_type,
    "metadata": metadata,
    "schema": schema,
    "profile": profile,
    "quality": quality,
    "issues": issues,
    "recommendations": recommendations,
    "type_suggestions": type_suggestions

}