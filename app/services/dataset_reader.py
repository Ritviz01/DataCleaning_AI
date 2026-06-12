# File encoding detect karne ke liye
from app.services.encoding_detector import detect_encoding

import polars as pl


def read_dataset(file_path: str, file_type: str):

    # CSV files
    if file_type == "csv":

        encoding = detect_encoding(file_path)

        print(f"Detected Encoding: {encoding}")

        return pl.read_csv(
            file_path,
            encoding=encoding,
            ignore_errors=True,
            try_parse_dates=True,
            null_values=["", "NA", "NULL", "null"]
        )

    # Excel files
    elif file_type == "excel":

        return pl.read_excel(file_path)

    # JSON files
    elif file_type == "json":

        return pl.read_json(file_path)

    # Parquet files
    elif file_type == "parquet":

        return pl.read_parquet(file_path)

    else:

        raise ValueError(
            f"Unsupported file type: {file_type}"
        )