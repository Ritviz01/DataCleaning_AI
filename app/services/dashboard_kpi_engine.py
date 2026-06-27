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
        name = kpi.get("name") or kpi.get("title") or "Metric"
        column = kpi.get("column")
        aggregation = kpi.get("aggregation", "count")
        priority = kpi.get("priority", "Medium")
        description = kpi.get("description", "")
        
        try:
            val = calculate_kpi_value(df, column, aggregation)
            if isinstance(val, float):
                val = round(val, 2)
        except Exception as e:
            print(f"Error calculating KPI '{name}' on column '{column}' via '{aggregation}': {e}")
            val = None
            
        results.append({
            "name": name,
            "title": name,
            "column": column,
            "aggregation": aggregation,
            "value": val,
            "priority": priority,
            "description": description
        })
        
    return results

def generate_kpis(df: pl.DataFrame, schema: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Automatically generate KPI cards with title, value, aggregation, and description."""
    kpis = []
    
    # 1. Total Records (always include)
    total_records = df.height
    kpis.append({
        "name": "Total Records",
        "title": "Total Records",
        "value": total_records,
        "aggregation": "count",
        "priority": "High",
        "description": "Total number of rows in the dataset."
    })
    
    for col in schema:
        col_name = col.get("column_name")
        dtype = col.get("data_type", "")
        semantic = col.get("semantic_type", "")
        
        if not col_name or col_name not in df.columns:
            continue
            
        col_lower = col_name.lower().strip()
        
        # Skip index and RECORD_ID columns
        if (
            semantic == "RECORD_ID"
            or col_lower == "unnamed: 0"
            or "unnamed" in col_lower
            or col_lower in ["index", "row", "row_id", "s.no", "sl_no", "serial_number"]
        ):
            continue
        
        # ID Columns
        if semantic == "ID" or "id" in col_lower:
            try:
                unique_ids = df[col_name].n_unique()
                kpis.append({
                    "name": f"Unique {col_name}",
                    "title": f"Unique {col_name}",
                    "column": col_name,
                    "value": unique_ids,
                    "aggregation": "unique_count",
                    "priority": "High" if "id" in col_lower else "Medium",
                    "description": f"Total number of unique values in {col_name}."
                })
            except Exception:
                pass
                
        # Price Columns
        elif semantic == "PRICE" or "price" in col_lower or "cost" in col_lower or "amount" in col_lower:
            try:
                avg_price = df[col_name].cast(pl.Float64, strict=False).mean()
                max_price = df[col_name].cast(pl.Float64, strict=False).max()
                if avg_price is not None:
                    kpis.append({
                        "name": f"Average {col_name}",
                        "title": f"Average {col_name}",
                        "column": col_name,
                        "value": round(float(avg_price), 2),
                        "aggregation": "mean",
                        "priority": "High",
                        "description": f"The average value of {col_name}."
                    })
                if max_price is not None:
                    kpis.append({
                        "name": f"Highest {col_name}",
                        "title": f"Highest {col_name}",
                        "column": col_name,
                        "value": round(float(max_price), 2),
                        "aggregation": "max",
                        "priority": "Medium",
                        "description": f"The maximum value of {col_name}."
                    })
            except Exception:
                pass
                
        # Date Columns
        elif semantic == "DATE" or "date" in col_lower or "time" in col_lower or "dob" in col_lower:
            try:
                non_null = df[col_name].drop_nulls()
                if non_null.len() > 0:
                    earliest = non_null.min()
                    latest = non_null.max()
                    if earliest is not None:
                        kpis.append({
                            "name": f"Earliest {col_name}",
                            "title": f"Earliest {col_name}",
                            "column": col_name,
                            "value": str(earliest),
                            "aggregation": "min",
                            "priority": "Medium",
                            "description": f"The earliest date in {col_name}."
                        })
                    if latest is not None:
                        kpis.append({
                            "name": f"Latest {col_name}",
                            "title": f"Latest {col_name}",
                            "column": col_name,
                            "value": str(latest),
                            "aggregation": "max",
                            "priority": "Medium",
                            "description": f"The latest date in {col_name}."
                        })
            except Exception:
                pass
                
        # Numeric Columns (other than price/date/id)
        elif dtype in ("Int64", "Float64", "Int32", "Float32", "Int16", "Int8", "UInt64", "UInt32") or semantic in ("AGE", "MEASUREMENT", "COUNT", "RATING", "DURATION"):
            try:
                series = df[col_name].cast(pl.Float64, strict=False)
                mean_val = series.mean()
                min_val = series.min()
                max_val = series.max()
                sum_val = series.sum()
                
                is_measurement_or_rating = (
                    semantic in ("MEASUREMENT", "RATING")
                    or any(k in col_lower for k in ["weight", "rating", "rating_score", "inches", "size"])
                )
                
                if mean_val is not None:
                    kpis.append({
                        "name": f"Average {col_name}",
                        "title": f"Average {col_name}",
                        "column": col_name,
                        "value": round(float(mean_val), 2),
                        "aggregation": "mean",
                        "priority": "Medium",
                        "description": f"The average value of {col_name}."
                    })
                
                if is_measurement_or_rating:
                    if min_val is not None:
                        kpis.append({
                            "name": f"Minimum {col_name}",
                            "title": f"Minimum {col_name}",
                            "column": col_name,
                            "value": round(float(min_val), 2),
                            "aggregation": "min",
                            "priority": "Medium",
                            "description": f"The minimum value of {col_name}."
                        })
                    if max_val is not None:
                        kpis.append({
                            "name": f"Maximum {col_name}",
                            "title": f"Maximum {col_name}",
                            "column": col_name,
                            "value": round(float(max_val), 2),
                            "aggregation": "max",
                            "priority": "Medium",
                            "description": f"The maximum value of {col_name}."
                        })
                else:
                    if sum_val is not None:
                        kpis.append({
                            "name": f"Total {col_name}",
                            "title": f"Total {col_name}",
                            "column": col_name,
                            "value": round(float(sum_val), 2),
                            "aggregation": "sum",
                            "priority": "High",
                            "description": f"The sum total of {col_name}."
                        })
            except Exception:
                pass
                
        # Categorical / String Columns
        elif dtype == "String" or semantic in ("CATEGORY", "COMPANY", "DEPARTMENT", "GENDER", "COUNTRY", "CITY", "STATE", "STATUS"):
            try:
                unique_vals = df[col_name].n_unique()
                kpis.append({
                    "name": f"Unique {col_name}",
                    "title": f"Unique {col_name}",
                    "column": col_name,
                    "value": unique_vals,
                    "aggregation": "unique_count",
                    "priority": "Medium",
                    "description": f"Total number of unique {col_name} segments."
                })
            except Exception:
                pass
                
    return kpis
