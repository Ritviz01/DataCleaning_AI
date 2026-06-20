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

router = APIRouter(prefix="/datasets", tags=["datasets"])
UPLOAD_DIR = Path("uploads").resolve()
EXPORT_DIR = Path("exports").resolve()
MAX_UPLOAD_BYTES = 100 * 1024 * 1024


def _safe_filename(filename: str | None) -> str:
    name = Path(filename or "dataset").name
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


async def _store_upload(file: UploadFile) -> tuple[Path, str, str]:
    filename = _safe_filename(file.filename)
    file_type = detect_file_type(filename)
    if file_type == "unknown":
        raise HTTPException(status_code=415, detail="Supported formats: CSV, XLSX, XLS, JSON, and Parquet.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIR / f"{uuid.uuid4().hex}_{filename}"
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


async def _read_upload(file: UploadFile) -> tuple[pl.DataFrame, str]:
    path, filename, file_type = await _store_upload(file)
    try:
        dataframe = clean_column_names(read_dataset(str(path), file_type))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not read this dataset: {exc}") from exc
    if dataframe.width == 0:
        raise HTTPException(status_code=422, detail="Dataset has no columns.")
    return dataframe, filename


@router.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Return a non-destructive quality report and proposed cleaning actions."""
    dataframe, filename = await _read_upload(file)
    return {"filename": filename, "analysis": analyse_dataset(dataframe)}


@router.post("/clean")
async def clean_file(file: UploadFile = File(...)):
    """Apply the engine's recommendations and provide a downloadable CSV.

    This remains a conservative baseline; sensitive identifier and invalid-value
    problems are returned as manual-review recommendations rather than altered.
    """
    dataframe, filename = await _read_upload(file)
    before = analyse_dataset(dataframe)
    cleaned, audit_log = clean_dataset(dataframe, before["recommendations"])
    after = analyse_dataset(cleaned)

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export_name = f"cleaned_{uuid.uuid4().hex}_{Path(filename).stem}.csv"
    cleaned.write_csv(EXPORT_DIR / export_name)

    return {
        "filename": filename,
        "before": before,
        "after": after,
        "cleaning_log": audit_log,
        "export": {"filename": export_name, "download_url": f"/exports/{export_name}"},
    }


# Backwards-compatible name for clients that started with the original prototype.
@router.post("/upload", deprecated=True)
async def upload_file(file: UploadFile = File(...)):
    return await analyze_file(file)
