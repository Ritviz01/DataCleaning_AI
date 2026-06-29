import time
import json
import polars as pl
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple
from app.services.pipeline_engine.transformation_registry import registry

@dataclass
class ExecutionStepResult:
    transformation: str
    status: str  # 'success', 'failed'
    started_at: float  # epoch time
    duration_ms: float
    rows_before: int
    rows_after: int
    rows_affected: int
    columns_affected: List[str]
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

def execute_step(
    df: pl.DataFrame,
    transformation: str,
    params: Dict[str, Any]
) -> Tuple[pl.DataFrame, ExecutionStepResult]:
    started_at = time.time()
    rows_before = df.height
    columns_before = set(df.columns)
    
    try:
        handler = registry.get(transformation)
        # Deep clone to avoid mutating in-place or in case of partial failure
        df_clone = df.clone()
        
        # Execute the handler
        df_after = handler(df_clone, params)
        duration_ms = (time.time() - started_at) * 1000
        
        rows_after = df_after.height
        columns_after = set(df_after.columns)
        
        # Determine columns affected
        columns_affected = []
        # 1. Dropped columns
        dropped = columns_before - columns_after
        columns_affected.extend(list(dropped))
        # 2. Added columns
        added = columns_after - columns_before
        columns_affected.extend(list(added))
        # 3. Modified columns (present in both but content/type differs)
        overlapping = columns_before & columns_after
        modified = []
        
        rows_affected = 0
        
        if rows_before != rows_after:
            rows_affected = abs(rows_before - rows_after)
            # If row count changed (e.g. remove_duplicates, remove_outliers filter), columns are not necessarily "modified" in their values per row but their dataset structure changed. Let's still mark the overlapping columns if they were part of subset or check if they changed.
        else:
            # Check row-by-row differences for overlapping columns
            any_diff_expr = None
            for col in overlapping:
                # First check if the column is identical (fast path)
                if not df[col].equals(df_after[col]):
                    modified.append(col)
                    col_diff = (pl.col(col) != df_after[col]) | (pl.col(col).is_null() != df_after[col].is_null())
                    any_diff_expr = col_diff if any_diff_expr is None else any_diff_expr | col_diff
            
            if any_diff_expr is not None:
                rows_affected = df.filter(any_diff_expr).height
            
            columns_affected.extend(modified)
            
        # Clean duplicates in columns affected
        columns_affected = list(set(columns_affected))
        
        details = {
            "columns_dropped": list(dropped),
            "columns_added": list(added),
            "columns_modified": modified,
            "params": params
        }
        
        result = ExecutionStepResult(
            transformation=transformation,
            status="success",
            started_at=started_at,
            duration_ms=round(duration_ms, 2),
            rows_before=rows_before,
            rows_after=rows_after,
            rows_affected=rows_affected,
            columns_affected=columns_affected,
            details=details
        )
        return df_after, result
        
    except Exception as e:
        duration_ms = (time.time() - started_at) * 1000
        result = ExecutionStepResult(
            transformation=transformation,
            status="failed",
            started_at=started_at,
            duration_ms=round(duration_ms, 2),
            rows_before=rows_before,
            rows_after=rows_before,
            rows_affected=0,
            columns_affected=[],
            error_message=str(e),
            details={"params": params, "error_type": type(e).__name__}
        )
        return df, result
