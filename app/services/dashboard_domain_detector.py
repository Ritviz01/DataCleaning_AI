import polars as pl
from app.services.dataset_classifier import classify_dataset

def detect_domain(df: pl.DataFrame, schema: list[dict]) -> str:
    """Detects the dataset's business domain using metadata, columns, and LLM classification.
    
    Args:
        df: The Polars DataFrame of the dataset.
        schema: The list of columns and their inferred data/semantic types.
        
    Returns:
        The detected domain name (e.g. Sales, HR, Healthcare, Education, Finance, etc.).
    """
    metadata = {
        "columns": df.columns,
        "rows": df.height,
        "column_names": df.columns
    }
    
    classification = classify_dataset(metadata, df.columns, schema)
    return classification.get("dataset_type", "General")
