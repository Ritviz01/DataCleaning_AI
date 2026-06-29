import polars as pl
from typing import Dict, Any, List
from app.services.pipeline_engine.transformation_executor import execute_step

def preview_pipeline_execution(df: pl.DataFrame, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simulates pipeline execution without modifying the stored dataset.
    Returns preview metadata and sample rows of before/after.
    """
    original_df = df
    current_df = df.clone()
    
    changed_columns_set = set()
    
    # Execute steps sequentially on cloned df
    for step in steps:
        transformation = step.get("transformation")
        params = step.get("params") or {}
        
        # Execute using execute_step
        current_df, step_res = execute_step(current_df, transformation, params)
        if step_res.status == "success":
            changed_columns_set.update(step_res.columns_affected)
            
    # Calculate row differences
    rows_changed = 0
    if original_df.height != current_df.height:
        rows_changed = abs(original_df.height - current_df.height)
    else:
        # Compare cells for row modifications
        overlapping = set(original_df.columns) & set(current_df.columns)
        any_diff_expr = None
        for col in overlapping:
            if not original_df[col].equals(current_df[col]):
                col_diff = (pl.col(col) != current_df[col]) | (pl.col(col).is_null() != current_df[col].is_null())
                any_diff_expr = col_diff if any_diff_expr is None else any_diff_expr | col_diff
        if any_diff_expr is not None:
            rows_changed = original_df.filter(any_diff_expr).height

    # Calculate total modified cell values
    cell_mods = 0
    dropped_cols = set(original_df.columns) - set(current_df.columns)
    added_cols = set(current_df.columns) - set(original_df.columns)
    overlapping_cols = set(original_df.columns) & set(current_df.columns)
    
    cell_mods += len(dropped_cols) * original_df.height
    cell_mods += len(added_cols) * current_df.height
    
    if original_df.height == current_df.height:
        for col in overlapping_cols:
            if not original_df[col].equals(current_df[col]):
                diff_mask = (original_df[col] != current_df[col]) | (original_df[col].is_null() != current_df[col].is_null())
                cell_mods += original_df.filter(diff_mask).height
    else:
        min_len = min(original_df.height, current_df.height)
        height_diff = abs(original_df.height - current_df.height)
        cell_mods += height_diff * len(overlapping_cols)
        for col in overlapping_cols:
            col_orig_slice = original_df[col].head(min_len)
            col_curr_slice = current_df[col].head(min_len)
            if not col_orig_slice.equals(col_curr_slice):
                temp_df = pl.DataFrame({"c1": col_orig_slice, "c2": col_curr_slice})
                diff_count = temp_df.filter((pl.col("c1") != pl.col("c2")) | (pl.col("c1").is_null() != pl.col("c2").is_null())).height
                cell_mods += diff_count

    # Sample rows (first 100 rows)
    orig_sample = original_df.head(100).to_dicts()
    trans_sample = current_df.head(100).to_dicts()

    return {
        "changed_rows": rows_changed,
        "changed_columns": list(changed_columns_set),
        "modified_values_count": cell_mods,
        "original_sample": orig_sample,
        "transformed_sample": trans_sample,
        "original_schema": [
            {"column_name": c, "type": str(original_df[c].dtype)}
            for c in original_df.columns
        ],
        "transformed_schema": [
            {"column_name": c, "type": str(current_df[c].dtype)}
            for c in current_df.columns
        ]
    }
