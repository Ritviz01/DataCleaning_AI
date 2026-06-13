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
# Auto Cleaner
from app.services.auto_cleaner import auto_clean_dataset



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

    # DEBUG
    print("\n===== DATASET HEAD =====")
    print(df.head(10))

    print("\n===== SCHEMA =====")
    print(df.schema)

    if "Enrollment_Date" in df.columns:
        print("\n===== ENROLLMENT DATE SAMPLE =====")
        print(df["Enrollment_Date"].head(20))

    if "First_Name" in df.columns:
        print("\n===== FIRST NAME SAMPLE =====")
        print(df["First_Name"].head(20))

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

    # Infer better data types
    type_suggestions = infer_better_types(df)

    # Generate cleaning recommendations
    recommendations = generate_recommendations(
        issues,
        schema,
        type_suggestions
    )

    # Apply cleaning actions
    cleaned_df, cleaning_log = auto_clean_dataset(
        df,
        recommendations
    )
    # Profile after cleaning
    cleaned_profile = profile_dataset(cleaned_df)

    # Detect issues after cleaning
    cleaned_issues = detect_issues(cleaned_df)

    # Quality score after cleaning
    cleaned_quality = calculate_quality_score(
        cleaned_issues
    )


    return {
    "filename": file.filename,
    "file_type": file_type,
    "metadata": metadata,
    "schema": schema,
    "profile": profile,
    "quality": quality,
    "issues": issues,
    "recommendations": recommendations,
    "type_suggestions": type_suggestions,
    "cleaning_log": cleaning_log,
    
    "after_cleaning": {
        "profile": cleaned_profile,
        "issues": cleaned_issues,
        "quality": cleaned_quality
    }
}