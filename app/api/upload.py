from fastapi import APIRouter, UploadFile, File
import os
import shutil

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
from app.services.llm_insights import (
    generate_llm_insights
)

# NEW
from app.services.semantic_cleaner import (
    semantic_clean_dataset
)

from app.services.type_converter import (
    apply_type_conversions
)

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # ==========================
    # FILE TYPE
    # ==========================

    file_type = detect_file_type(
        file.filename
    )

    # ==========================
    # READ DATASET
    # ==========================

    df = read_dataset(
        file_path,
        file_type
    )

    # ==========================
    # CLEAN COLUMN NAMES
    # ==========================

    df = clean_column_names(df)

    # ==========================
    # SEMANTIC CLEANING
    # ==========================

    df = semantic_clean_dataset(df)

    # ==========================
    # METADATA
    # ==========================

    metadata = generate_metadata(df)

    # ==========================
    # SCHEMA
    # ==========================

    schema = infer_schema(df)

    # ==========================
    # PROFILE
    # ==========================

    profile = profile_dataset(df)

    # ==========================
    # TYPE SUGGESTIONS
    # ==========================

    type_suggestions = (
        infer_better_types(df)
    )

    # ==========================
    # TYPE CONVERSION
    # ==========================

    df = apply_type_conversions(
        df,
        type_suggestions
    )

    # ==========================
    # ISSUES
    # ==========================

    issues = detect_issues(df)

    # ==========================
    # QUALITY
    # ==========================

    quality = calculate_quality_score(
        profile,
        issues
    )

    # ==========================
    # RECOMMENDATIONS
    # ==========================

    recommendations = (
        generate_recommendations(
            issues,
            schema,
            type_suggestions
        )
    )

    # ==========================
    # AUTO CLEANING
    # ==========================

    cleaned_df, cleaning_log = (
        auto_clean_dataset(
            df,
            recommendations
        )
    )

    # ==========================
    # AFTER CLEANING PROFILE
    # ==========================

    cleaned_profile = (
        profile_dataset(
            cleaned_df
        )
    )

    # ==========================
    # AFTER CLEANING ISSUES
    # ==========================

    cleaned_issues = (
        detect_issues(
            cleaned_df
        )
    )

    # ==========================
    # AFTER CLEANING QUALITY
    # ==========================

    cleaned_quality = (
        calculate_quality_score(
            cleaned_profile,
            cleaned_issues
        )
    )
    llm_insights = generate_llm_insights(
        metadata,
        quality,
        issues,
        schema
    )

    return {

        "filename":
        file.filename,

        "file_type":
        file_type,

        "metadata":
        metadata,

        "schema":
        schema,

        "profile":
        profile,

        "quality":
        quality,

        "issues":
        issues,

        "recommendations":
        recommendations,

        "type_suggestions":
        type_suggestions,

        "cleaning_log":
        cleaning_log,

        "after_cleaning": {

            "profile":
            cleaned_profile,

            "issues":
            cleaned_issues,

            "quality":
            cleaned_quality
        },
        "llm_insights":
          llm_insights,
    }