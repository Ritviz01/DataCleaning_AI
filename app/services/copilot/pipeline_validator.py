import polars as pl
from typing import Dict, Any, List
from app.services.pipeline_engine.pipeline_validator import validate_pipeline

def validate_copilot_pipeline(df: pl.DataFrame, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a copilot-generated pipeline before execution.
    Reuse the existing pipeline engine validator, adding extra compatibility checks.
    """
    steps = pipeline_data.get("steps") or []
    
    # Call core pipeline engine validator
    is_valid, errors, warnings = validate_pipeline(df, steps)
    
    # Add custom Copilot validation rules
    dropped_cols = set()
    column_renames = {}
    
    for idx, step in enumerate(steps):
        order = step.get("order", idx + 1)
        trans = step.get("transformation")
        params = step.get("params") or {}
        
        if trans == "rename_column":
            col = params.get("column")
            new_name = params.get("new_name")
            if col and new_name:
                # Check renaming to existing active column
                if new_name in df.columns and new_name not in dropped_cols and col != new_name:
                    errors.append({
                        "step_index": order,
                        "field": "new_name",
                        "message": f"Incompatible rename: target column name '{new_name}' already exists and is active."
                    })
                # Check circular rename
                if column_renames.get(new_name) == col:
                    errors.append({
                        "step_index": order,
                        "field": "column",
                        "message": f"Circular rename dependency: renaming '{col}' to '{new_name}' reverses a previous step."
                    })
                column_renames[col] = new_name
                
        elif trans == "drop_column":
            col = params.get("column")
            if col:
                dropped_cols.add(col)
                
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
