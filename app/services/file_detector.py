from pathlib import Path


SUPPORTED_TYPES = {
    ".csv": "csv",
    ".xlsx": "excel",
    ".xls": "excel",
    ".json": "json",
    ".parquet": "parquet"
}


def detect_file_type(filename: str):
    extension = Path(filename).suffix.lower()

    return SUPPORTED_TYPES.get(extension, "unknown")