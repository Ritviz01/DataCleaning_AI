import polars as pl


def read_dataset(file_path: str, file_type: str):

    if file_type == "csv":
        return pl.read_csv(file_path)

    elif file_type == "excel":
        return pl.read_excel(file_path)

    elif file_type == "json":
        return pl.read_json(file_path)

    elif file_type == "parquet":
        return pl.read_parquet(file_path)

    else:
        raise ValueError(f"Unsupported file type: {file_type}")