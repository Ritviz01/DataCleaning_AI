import polars as pl
import json
from typing import Dict, Any, List, Tuple
from app.services.pipeline_engine.transformation_registry import registry

def validate_pipeline(df: pl.DataFrame, steps: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validates a list of pipeline steps against a dataframe.
    Returns: (is_valid, errors, warnings)
    errors format: [{"step_index": int, "field": str, "message": str}]
    warnings format: [{"step_index": int, "message": str}]
    """
    errors = []
    warnings = []
    
    # Track simulated schema state
    # We copy list of columns to simulate mutations step by step
    current_columns = list(df.columns)
    
    # Helper to check if columns exist in current columns
    def col_exists(col: str) -> bool:
        return col in current_columns

    previous_step = None
    
    for idx, step in enumerate(steps):
        step_index = step.get("order", idx + 1)
        transformation = step.get("transformation")
        params = step.get("params") or {}
        
        # Check duplicate step warning
        current_step_sig = (transformation, json_serialize_params(params))
        if previous_step == current_step_sig:
            warnings.append({
                "step_index": step_index,
                "message": f"Step {step_index} is a duplicate of the previous step with identical parameters."
            })
        previous_step = current_step_sig

        # 1. Unknown transformation
        try:
            registry.get(transformation)
        except ValueError:
            errors.append({
                "step_index": step_index,
                "field": "transformation",
                "message": f"Unknown transformation '{transformation}'"
            })
            continue

        # 2. Parameter & schema checks
        if transformation == "remove_duplicates":
            subset = params.get("subset")
            if subset:
                sub_list = [subset] if isinstance(subset, str) else subset
                if not isinstance(sub_list, list):
                    errors.append({
                        "step_index": step_index,
                        "field": "subset",
                        "message": "subset must be a string or a list of strings"
                    })
                else:
                    for col in sub_list:
                        if not col_exists(col):
                            errors.append({
                                "step_index": step_index,
                                "field": "subset",
                                "message": f"Column '{col}' not found in current schema"
                            })

        elif transformation == "fill_missing":
            column = params.get("column")
            method = params.get("method", "value")
            if not column:
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": "Missing required parameter 'column'"
                })
            elif not col_exists(column):
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": f"Column '{column}' not found in current schema"
                })
            
            if method not in ["median", "mode", "forward_fill", "value"]:
                errors.append({
                    "step_index": step_index,
                    "field": "method",
                    "message": f"Invalid method '{method}'. Must be one of: median, mode, forward_fill, value"
                })
            
            if method == "value" and "fill_value" not in params:
                errors.append({
                    "step_index": step_index,
                    "field": "fill_value",
                    "message": "Missing required parameter 'fill_value' when method is 'value'"
                })

        elif transformation == "drop_column":
            column = params.get("column")
            if not column:
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": "Missing required parameter 'column'"
                })
            elif not col_exists(column):
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": f"Column '{column}' not found in current schema"
                })
            else:
                # Simulate drop
                current_columns.remove(column)

        elif transformation == "rename_column":
            column = params.get("column")
            new_name = params.get("new_name")
            if not column:
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": "Missing required parameter 'column'"
                })
            elif not col_exists(column):
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": f"Column '{column}' not found in current schema"
                })
            if not new_name:
                errors.append({
                    "step_index": step_index,
                    "field": "new_name",
                    "message": "Missing required parameter 'new_name'"
                })
            
            if column and new_name and col_exists(column):
                # Simulate rename
                idx_col = current_columns.index(column)
                current_columns[idx_col] = new_name

        elif transformation == "convert_type":
            column = params.get("column")
            target_type = params.get("target_type") or params.get("suggested_type")
            if not column:
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": "Missing required parameter 'column'"
                })
            elif not col_exists(column):
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": f"Column '{column}' not found in current schema"
                })
            if not target_type:
                errors.append({
                    "step_index": step_index,
                    "field": "target_type",
                    "message": "Missing required parameter 'target_type'"
                })
            elif target_type not in ["Integer", "Float", "Date", "Boolean", "Integer-like", "Float-like"]:
                errors.append({
                    "step_index": step_index,
                    "field": "target_type",
                    "message": f"Invalid target_type '{target_type}'. Must be one of: Integer, Float, Date, Boolean, Integer-like, Float-like"
                })

        elif transformation in ["remove_outliers", "normalize", "encode_categories"]:
            column = params.get("column")
            if not column:
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": "Missing required parameter 'column'"
                })
            elif not col_exists(column):
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": f"Column '{column}' not found in current schema"
                })
            
            if transformation == "remove_outliers":
                method = params.get("method", "cap")
                if method not in ["cap", "remove"]:
                    errors.append({
                        "step_index": step_index,
                        "field": "method",
                        "message": f"Invalid method '{method}'. Must be one of: cap, remove"
                    })
            elif transformation == "normalize":
                method = params.get("method", "min_max")
                if method not in ["min_max", "z_score"]:
                    errors.append({
                        "step_index": step_index,
                        "field": "method",
                        "message": f"Invalid method '{method}'. Must be one of: min_max, z_score"
                    })
            elif transformation == "encode_categories":
                method = params.get("method", "label")
                if method not in ["label", "one_hot"]:
                    errors.append({
                        "step_index": step_index,
                        "field": "method",
                        "message": f"Invalid method '{method}'. Must be one of: label, one_hot"
                    })
                
                # Simulate categorical encoding
                if column and col_exists(column):
                    if method == "one_hot":
                        # We need unique values to simulate added columns.
                        # Since we can query the actual dataframe (if the column exists in the initial df)
                        if column in df.columns:
                            try:
                                unique_vals = df[column].drop_nulls().unique().to_list()
                                # Simulate adding {column}_{val} and dropping {column}
                                current_columns.remove(column)
                                for val in unique_vals:
                                    current_columns.append(f"{column}_{val}")
                            except Exception:
                                # Fallback if fails
                                current_columns.remove(column)
                                current_columns.append(f"{column}_encoded")
                        else:
                            # It's a dynamically added column, fallback simulation
                            current_columns.remove(column)
                            current_columns.append(f"{column}_encoded")

        elif transformation in ["standardize_text", "trim_whitespace"]:
            column = params.get("column")
            if column and not col_exists(column):
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": f"Column '{column}' not found in current schema"
                })

        elif transformation in ["lowercase", "uppercase"]:
            column = params.get("column")
            if not column:
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": "Missing required parameter 'column'"
                })
            elif not col_exists(column):
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": f"Column '{column}' not found in current schema"
                })

        elif transformation == "replace_values":
            column = params.get("column")
            if not column:
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": "Missing required parameter 'column'"
                })
            elif not col_exists(column):
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": f"Column '{column}' not found in current schema"
                })
            if "old_value" not in params or "new_value" not in params:
                errors.append({
                    "step_index": step_index,
                    "field": "params",
                    "message": "Missing required parameters 'old_value' and/or 'new_value'"
                })

        elif transformation == "split_column":
            column = params.get("column")
            new_columns = params.get("new_columns")
            if not column:
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": "Missing required parameter 'column'"
                })
            elif not col_exists(column):
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": f"Column '{column}' not found in current schema"
                })
            if not new_columns or not isinstance(new_columns, list):
                errors.append({
                    "step_index": step_index,
                    "field": "new_columns",
                    "message": "Missing required parameter 'new_columns' or it is not a list"
                })
            
            if column and col_exists(column) and new_columns and isinstance(new_columns, list):
                # Simulate split: drop column, add new_columns
                current_columns.remove(column)
                current_columns.extend(new_columns)

        elif transformation == "merge_columns":
            columns = params.get("columns")
            new_column = params.get("new_column")
            if not columns or not isinstance(columns, list):
                errors.append({
                    "step_index": step_index,
                    "field": "columns",
                    "message": "Missing required parameter 'columns' or it is not a list"
                })
            else:
                for col in columns:
                    if not col_exists(col):
                        errors.append({
                            "step_index": step_index,
                            "field": "columns",
                            "message": f"Column '{col}' not found in current schema"
                        })
            if not new_column:
                errors.append({
                    "step_index": step_index,
                    "field": "new_column",
                    "message": "Missing required parameter 'new_column'"
                })
            
            if new_column:
                current_columns.append(new_column)

        elif transformation == "feature_engineering":
            column = params.get("column")
            operation = params.get("operation")
            if not column:
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": "Missing required parameter 'column'"
                })
            elif not col_exists(column):
                errors.append({
                    "step_index": step_index,
                    "field": "column",
                    "message": f"Column '{column}' not found in current schema"
                })
            if not operation or operation not in ["log", "square", "sqrt", "bin"]:
                errors.append({
                    "step_index": step_index,
                    "field": "operation",
                    "message": "Missing required parameter 'operation' or it is invalid. Must be log, square, sqrt, or bin"
                })
            
            if column and col_exists(column) and operation:
                # Simulate added column
                suffix = {
                    "log": "_log",
                    "square": "_sq",
                    "sqrt": "_sqrt",
                    "bin": "_binned"
                }.get(operation, "_feat")
                current_columns.append(f"{column}{suffix}")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings

def json_serialize_params(params: Dict[str, Any]) -> str:
    try:
        return json.dumps(params, sort_keys=True)
    except Exception:
        return str(params)

