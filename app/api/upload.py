"""Upload, analyse, and explicitly clean tabular datasets."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

import polars as pl
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.column_cleaner import clean_column_names
from app.services.dataset_reader import read_dataset
from app.services.file_detector import detect_file_type
from app.services.pipeline import analyse_dataset, clean_dataset
from app.services.dataset_store import dataset_store

router = APIRouter(prefix="/datasets", tags=["datasets"])
UPLOAD_DIR = Path("uploads").resolve()
EXPORT_DIR = Path("exports").resolve()
MAX_UPLOAD_BYTES = 100 * 1024 * 1024


def _safe_filename(filename: str | None) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename or "dataset").name)


async def _store_upload(file: UploadFile, dataset_id: str) -> tuple[Path, str, str]:
    filename = _safe_filename(file.filename)
    file_type = detect_file_type(filename)
    if file_type == "unknown":
        raise HTTPException(status_code=415, detail="Supported formats: CSV, XLSX, XLS, JSON, and Parquet.")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIR / f"{dataset_id}_{filename}"
    size = 0
    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="File exceeds the 100 MB upload limit.")
                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
    return destination, filename, file_type


async def _read_upload(file: UploadFile, dataset_id: str) -> tuple[pl.DataFrame, str, Path]:
    path, filename, file_type = await _store_upload(file, dataset_id)
    try:
        dataframe = clean_column_names(read_dataset(str(path), file_type))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not read this dataset: {exc}") from exc
    if dataframe.width == 0:
        raise HTTPException(status_code=422, detail="Dataset has no columns.")
    return dataframe, filename, path


def enrich_analysis_response(analysis: dict) -> dict:
    from app.services.dataset_classifier import classify_dataset
    from app.services.kpi_generator import generate_kpis
    from app.services.chart_recommender import recommend_charts
    from app.services.human_review_engine import generate_review_flags
    from app.services.data_dictionary import generate_dictionary
    from app.services.sql_generator import generate_sql_queries
    from app.services.report_generator import generate_report

    metadata = analysis.get("metadata", {})
    schema = analysis.get("schema", [])
    issues = analysis.get("issues", [])
    quality = analysis.get("quality", {})
    
    # 1. Dataset type classification
    class_res = classify_dataset(metadata, metadata.get("column_names", []), schema)
    dataset_type = class_res.get("dataset_type", "General")
    
    # 2. Recommended KPIs
    kpis = generate_kpis(dataset_type, schema)
    
    # 3. Recommended charts
    charts = recommend_charts(schema)
    
    # 4. Human review flags
    review_flags = generate_review_flags(issues, schema, analysis.get("type_suggestions"))
    
    # 5. Data dictionary
    data_dict = generate_dictionary(schema, metadata)
    
    # 6. SQL queries
    sql_queries = generate_sql_queries(schema, dataset_type)
    
    # 7. Executive report
    report = generate_report(metadata, quality, issues, kpis, charts, dataset_type, schema)
    
    return {
        "dataset_type": dataset_type,
        "recommended_kpis": kpis,
        "recommended_charts": charts,
        "human_review_flags": review_flags,
        "data_dictionary": data_dict,
        "sql_queries": sql_queries,
        "executive_report": report
    }


@router.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Return a non-destructive quality report and proposed cleaning actions."""
    dataset_id = uuid.uuid4().hex[:12]
    dataframe, filename, path = await _read_upload(file, dataset_id)
    analysis = analyse_dataset(dataframe)
    
    quality_score = analysis.get("quality", {}).get("quality_score")
    issues = analysis.get("issues", [])
    
    dataset_store.store(
        dataframe,
        file_path=path,
        dataset_id=dataset_id,
        status="analyzed",
        quality_score=quality_score,
        issues=issues
    )
    
    from app.services.dashboard_service import generate_dashboard, save_dashboard_to_db
    dashboard = generate_dashboard(
        dataframe,
        analysis["schema"],
        analysis["profile"],
        analysis["insights"]
    )
    save_dashboard_to_db(dataset_id, dashboard)
    
    enrichment = enrich_analysis_response(analysis)
    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "analysis": analysis,
        "dashboard": dashboard,
        **enrichment
    }


@router.post("/clean")
async def clean_file(file: UploadFile = File(...)):
    """Apply recommendations and provide a downloadable cleaned CSV."""
    dataset_id = uuid.uuid4().hex[:12]
    dataframe, filename, path = await _read_upload(file, dataset_id)
    
    before = analyse_dataset(dataframe)
    before_quality_score = before.get("quality", {}).get("quality_score")
    before_issues = before.get("issues", [])
    
    dataset_store.store(
        dataframe,
        file_path=path,
        dataset_id=f"{dataset_id}_raw",
        status="uploaded",
        quality_score=before_quality_score,
        issues=before_issues
    )
    
    cleaned, audit_log = clean_dataset(dataframe, before["recommendations"])
    
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export_name = f"cleaned_{uuid.uuid4().hex}_{Path(filename).stem}.csv"
    export_path = EXPORT_DIR / export_name
    cleaned.write_csv(export_path)
    
    after = analyse_dataset(cleaned)
    after_quality_score = after.get("quality", {}).get("quality_score")
    after_issues = after.get("issues", [])
    
    dataset_store.store(
        cleaned,
        file_path=export_path,
        dataset_id=dataset_id,
        status="cleaned",
        quality_score=after_quality_score,
        issues=after_issues,
        audit_logs=audit_log
    )
    
    from app.services.dashboard_service import generate_dashboard, save_dashboard_to_db
    dashboard = generate_dashboard(
        cleaned,
        after["schema"],
        after["profile"],
        after["insights"]
    )
    save_dashboard_to_db(dataset_id, dashboard)
    
    enrichment = enrich_analysis_response(after)
    
    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "before": before,
        "after": after,
        "cleaning_log": audit_log,
        "export": {"filename": export_name, "download_url": f"/exports/{export_name}"},
        "dashboard": dashboard,
        **enrichment
    }


@router.post("/ai-insights")
async def ai_insights(file: UploadFile = File(...)):
    """Request an opt-in OpenAI explanation of aggregate quality findings."""
    dataset_id = uuid.uuid4().hex[:12]
    dataframe, filename, path = await _read_upload(file, dataset_id)
    
    analysis = analyse_dataset(dataframe)
    quality_score = analysis.get("quality", {}).get("quality_score")
    issues = analysis.get("issues", [])
    
    dataset_store.store(
        dataframe,
        file_path=path,
        dataset_id=dataset_id,
        status="analyzed",
        quality_score=quality_score,
        issues=issues
    )
    
    from app.services.business_insight_engine import generate_business_context
    from app.services.openai_service import generate_ai_insights
    
    business_context = generate_business_context(
        dataframe,
        analysis["schema"]
    )
    
    # Pack sample rows into business_context
    business_context["sample_rows"] = dataframe.head(10).to_dicts()
    
    try:
        insight = generate_ai_insights(
            analysis,
            business_context
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="OpenAI insight generation failed. Check the API key and account settings.") from exc
    return {"dataset_id": dataset_id, "filename": filename, "analysis": analysis, "ai_insight": insight}


@router.post("/upload", deprecated=True)
async def upload_file(file: UploadFile = File(...)):
    """Compatibility endpoint for the original prototype."""
    return await analyze_file(file)
