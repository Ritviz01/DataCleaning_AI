import polars as pl
from typing import Any, Dict, List

def execute_plan(plan: dict, df: pl.DataFrame) -> pl.DataFrame:
    """Executes a validated JSON query plan using Polars operations directly.
    
    No eval, exec, compile, globals, or dynamic python execution is performed.
    """
    steps = plan.get("steps")
    if not steps:
        if "operation" in plan:
            steps = [plan]
        else:
            raise ValueError("Query plan is empty.")

    current_df = df

    for step in steps:
        op = step.get("operation")

        if op == "filter":
            col = step["column"]
            operator = step["operator"]
            val = step["value"]
            current_df = _apply_filter(current_df, col, operator, val)

        elif op in ("groupby", "group_by"):
            group_cols = step["group"]
            if isinstance(group_cols, str):
                group_cols = [group_cols]
            target = step["target"]
            agg_func = step["aggregation"]
            current_df = _apply_groupby(current_df, group_cols, target, agg_func)

        elif op == "sort":
            col = step["column"]
            order = step.get("order", "ascending")
            descending = (order == "descending")
            current_df = current_df.sort(col, descending=descending)
            if "limit" in step and step["limit"] is not None:
                current_df = current_df.head(int(step["limit"]))

        elif op in ("head", "tail", "limit"):
            limit = step.get("limit") or step.get("value") or 10
            if op == "tail":
                current_df = current_df.tail(int(limit))
            else:
                current_df = current_df.head(int(limit))

        elif op == "unique":
            col = step["column"]
            current_df = current_df.select(col).unique()

        elif op == "value_counts":
            col = step["column"]
            current_df = current_df.select(col).value_counts(sort=True)

        elif op in ("mean", "median", "max", "min", "sum", "count"):
            col = step["column"]
            if op == "mean":
                current_df = current_df.select(pl.col(col).mean().alias(f"mean_{col}"))
            elif op == "median":
                current_df = current_df.select(pl.col(col).median().alias(f"median_{col}"))
            elif op == "max":
                current_df = current_df.select(pl.col(col).max().alias(f"max_{col}"))
            elif op == "min":
                current_df = current_df.select(pl.col(col).min().alias(f"min_{col}"))
            elif op == "sum":
                current_df = current_df.select(pl.col(col).sum().alias(f"sum_{col}"))
            elif op == "count":
                current_df = current_df.select(pl.col(col).count().alias(f"count_{col}"))

        elif op == "join":
            # Placeholder for future join capabilities
            pass

    return current_df


def _apply_filter(df: pl.DataFrame, col: str, operator: str, val: Any) -> pl.DataFrame:
    """Applies a filter operation on the dataframe using Polars expressions."""
    if operator in ("equals", "eq", "=="):
        return df.filter(pl.col(col) == val)
    elif operator in ("not_equals", "ne", "!="):
        return df.filter(pl.col(col) != val)
    elif operator in ("greater_than", "gt", ">"):
        return df.filter(pl.col(col) > val)
    elif operator in ("less_than", "lt", "<"):
        return df.filter(pl.col(col) < val)
    elif operator in ("greater_than_or_equal", "gte", ">="):
        return df.filter(pl.col(col) >= val)
    elif operator in ("less_than_or_equal", "lte", "<="):
        return df.filter(pl.col(col) <= val)
    elif operator in ("contains", "like"):
        return df.filter(pl.col(col).cast(pl.Utf8).str.contains(str(val)))
    elif operator == "in":
        if not isinstance(val, (list, tuple, set)):
            val = [val]
        return df.filter(pl.col(col).is_in(list(val)))
    else:
        raise ValueError(f"Unsupported filter operator: '{operator}'")


def _apply_groupby(df: pl.DataFrame, group_cols: List[str], target: str, agg_func: str) -> pl.DataFrame:
    """Applies a groupby and aggregation operation on the dataframe."""
    groupby_obj = df.group_by(group_cols)
    if agg_func == "mean":
        agg_expr = pl.col(target).mean().alias(f"mean_{target}")
    elif agg_func == "median":
        agg_expr = pl.col(target).median().alias(f"median_{target}")
    elif agg_func == "sum":
        agg_expr = pl.col(target).sum().alias(f"sum_{target}")
    elif agg_func == "min":
        agg_expr = pl.col(target).min().alias(f"min_{target}")
    elif agg_func == "max":
        agg_expr = pl.col(target).max().alias(f"max_{target}")
    elif agg_func in ("count", "n"):
        agg_expr = pl.col(target).count().alias(f"count_{target}")
    else:
        raise ValueError(f"Unsupported aggregation: '{agg_func}'")
        
    return groupby_obj.agg(agg_expr)


def execute_query(plan: dict, df: pl.DataFrame) -> dict:
    """Safe execution wrapper returning a standard success/result payload."""
    try:
        res_df = execute_plan(plan, df)
        return {
            "success": True,
            "result": res_df.to_dicts()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
