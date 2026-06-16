from fastapi import APIRouter, UploadFile, File
import os
import shutil

from app.services.outlier_detector import detect_outliers
from app.services.file_detector import detect_file_type
from app.services.dataset_reader import read_dataset
from app.services.metadata_service import generate_metadata
from app.services.schema_engine import infer_schema
from app.services.profiling_service import profile_dataset
from app.services.quality_score import calculate_quality_score
from app.services.issue_detector import detect_issues
from app.services.column_cleaner import clean_column_names
from app.services.recommendation_engine import generate_recommendations
from app.services.type_inference_engine import infer_better_types
from app.services.auto_cleaner import auto_clean_dataset

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    # File type detect
    file_type = detect_file_type(
        file.filename
    )

    # Read dataset
    df = read_dataset(
        file_path,
        file_type
    )

    # Clean column names
    df = clean_column_names(df)

    # Debug
    print("\n===== DATASET HEAD =====")
    print(df.head(10))

    print("\n===== SCHEMA =====")
    print(df.schema)

    # Metadata
    metadata = generate_metadata(df)

    # Schema
    schema = infer_schema(df)

    # Profile
    profile = profile_dataset(df)

    # Issues
    issues = detect_issues(df)

    # Outliers
    outlier_issues = detect_outliers(df)

    print("\n===== OUTLIERS =====")
    print(outlier_issues)

    issues.extend(outlier_issues)

    # Quality
    quality = calculate_quality_score(
        issues
    )

    # Type Suggestions
    type_suggestions = infer_better_types(
        df
    )

    # Recommendations
    recommendations = generate_recommendations(
        issues,
        schema,
        type_suggestions
    )

    # Auto Cleaning
    cleaned_df, cleaning_log = auto_clean_dataset(
        df,
        recommendations
    )

    # After Cleaning Profile
    cleaned_profile = profile_dataset(
        cleaned_df
    )

    # After Cleaning Issues
    cleaned_issues = detect_issues(
        cleaned_df
    )

    # Detect Outliers Again
    cleaned_outliers = detect_outliers(
        cleaned_df
    )

    cleaned_issues.extend(
        cleaned_outliers
    )

    # After Cleaning Quality
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