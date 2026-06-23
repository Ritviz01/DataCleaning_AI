"""The orchestration layer for a single, reproducible cleaning run."""

from __future__ import annotations

from typing import Any

import polars as pl

from app.services.auto_cleaner import auto_clean_dataset
from app.services.issue_detector import detect_issues
from app.services.metadata_service import generate_metadata
from app.services.profiling_service import profile_dataset
from app.services.quality_score import calculate_quality_score
from app.services.recommendation_engine import generate_recommendations
from app.services.schema_engine import infer_schema
from app.services.type_inference_engine import infer_better_types
from app.services.dataset_insight_engine import generate_dataset_insights


def analyse_dataset(df: pl.DataFrame) -> dict[str, Any]:
    """Profile a dataset without modifying it.

    Keeping analysis separate from cleaning is intentional: a caller can review
    every proposed change before it is applied.
    """
    metadata = generate_metadata(df)
    schema = infer_schema(df)
    profile = profile_dataset(df)
    type_suggestions = infer_better_types(df, schema)
    issues = detect_issues(df)
    quality = calculate_quality_score(profile, issues)
    recommendations = generate_recommendations(issues, schema, type_suggestions)

    return {
        "metadata": metadata,
        "schema": schema,
        "profile": profile,
        "quality": quality,
        "issues": issues,
        "recommendations": recommendations,
        "type_suggestions": type_suggestions,
        "insights": generate_dataset_insights(df, schema, metadata, quality, issues),
    }


def clean_dataset(df: pl.DataFrame, recommendations: list[dict[str, Any]]) -> tuple[pl.DataFrame, list[dict[str, Any]]]:
    """Apply only the explicit recommendations and return an audit log."""
    return auto_clean_dataset(df, recommendations)
