import polars as pl
from typing import Any, Dict, List

def calculate_kpi_value(df: pl.DataFrame, column: str, aggregation: str) -> Any:
    """Calculate a single KPI value from a Polars DataFrame.
    
    Args:
        df: Polars DataFrame.
        column: Column name to aggregate.
        aggregation: Aggregation function ('sum', 'mean', 'median', 'min', 'max', 'count', 'unique_count').
        
    Returns:
        The calculated aggregate scalar value.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in dataframe.")

    agg = aggregation.lower().strip()
    
    if agg == "sum":
        return df.select(pl.col(column).sum()).item()
    elif agg in ("mean", "average", "avg"):
        return df.select(pl.col(column).mean()).item()
    elif agg == "median":
        return df.select(pl.col(column).median()).item()
    elif agg in ("min", "minimum"):
        return df.select(pl.col(column).min()).item()
    elif agg in ("max", "maximum"):
        return df.select(pl.col(column).max()).item()
    elif agg == "count":
        return df.select(pl.col(column).count()).item()
    elif agg in ("unique_count", "n_unique", "unique"):
        return df.select(pl.col(column).n_unique()).item()
    else:
        raise ValueError(f"Unsupported aggregation: '{aggregation}'")

def calculate_kpis(kpis: List[Dict[str, Any]], df: pl.DataFrame) -> List[Dict[str, Any]]:
    """Calculates values for a list of KPI specifications using the DataFrame.
    
    Args:
        kpis: List of KPI spec dicts containing 'name', 'column', 'aggregation', and optional 'priority'.
        df: Polars DataFrame of the dataset.
        
    Returns:
        List of KPI specs updated with their calculated 'value'.
    """
    results = []
    for kpi in kpis:
        name = kpi.get("name", "Metric")
        column = kpi.get("column")
        aggregation = kpi.get("aggregation", "count")
        priority = kpi.get("priority", "Medium")
        
        try:
            val = calculate_kpi_value(df, column, aggregation)
            if isinstance(val, float):
                val = round(val, 2)
        except Exception as e:
            print(f"Error calculating KPI '{name}' on column '{column}' via '{aggregation}': {e}")
            val = None
            
        results.append({
            "name": name,
            "column": column,
            "aggregation": aggregation,
            "value": val,
            "priority": priority
        })
        
    return results
