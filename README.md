# DataClean AI

DataClean AI is a safe starting point for an AI-assisted data-cleaning platform.
It accepts common tabular data, profiles it, detects data-quality issues, proposes
cleaning steps, and can export a cleaned *copy* with an audit log. The original
upload is never overwritten.

## What works today

- CSV, Excel, JSON, and Parquet ingestion (up to 100 MB)
- Schema and semantic hints (ID, email, URL, dates, prices, categories, and text)
- Quality scoring, missing values, duplicate rows/IDs, invalid emails/dates, and
  IQR-based numeric outlier detection
- Conservative recommendation engine and logged cleaning export
- Protected upload filenames and protected export downloads

This is an analysis-and-rules foundation, not a trained universal model yet.
LLM or ML cleaning should be added as opt-in, reviewable stages after a reliable
benchmark dataset and evaluation criteria exist.

## Run locally

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open [the API documentation](http://127.0.0.1:8000/docs). The main workflow is:

1. `POST /datasets/analyze` with `multipart/form-data` field `file` to receive a
   non-destructive report and recommendations.
2. Review the response.
3. `POST /datasets/clean` with the same file to apply the conservative rules and
   get an export URL plus an audit log.

For compatibility with the original prototype, `POST /datasets/upload` remains
available and behaves like analysis only.

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Sensible next steps

- Add a frontend that lets users approve, reject, or edit individual recommendations.
- Store job metadata and audit logs in a database instead of local folders.
- Build labelled “dirty → expected clean” benchmark datasets for each domain.
- Add LLM reasoning only for ambiguous semantic fixes, with a confidence threshold,
  cost limit, PII policy, and human approval before changes are applied.
