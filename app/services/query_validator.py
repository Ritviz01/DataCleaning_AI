import polars as pl

def validate_plan(plan: dict, df: pl.DataFrame) -> None:
    """
    Validates a generated structured query plan.
    Raises ValueError if plan contains invalid operations, columns, or configurations.
    """
    if df is None:
        raise ValueError("Dataset does not exist or is empty.")
        
    steps = plan.get("steps")
    if not steps:
        if "operation" in plan:
            steps = [plan]
        else:
            raise ValueError("Query plan must contain 'steps' or a single 'operation'")

    allowed_ops = {
        "filter", "groupby", "group_by", "sort", "head", "tail", 
        "unique", "value_counts", "count", "mean", "median", 
        "max", "min", "sum", "limit"
    }

    for idx, step in enumerate(steps):
        op = step.get("operation")
        if not op:
            raise ValueError(f"Step {idx} is missing the 'operation' field.")
            
        if op not in allowed_ops:
            raise ValueError(f"Step {idx} contains unsupported operation: '{op}'")

        # 1. Validate referenced columns exist
        columns_to_check = []
        if "column" in step:
            columns_to_check.append(step["column"])
        if "target" in step:
            columns_to_check.append(step["target"])
        if "group" in step:
            g = step["group"]
            if isinstance(g, list):
                columns_to_check.extend(g)
            elif isinstance(g, str):
                columns_to_check.append(g)

        for col in columns_to_check:
            if col not in df.columns:
                raise ValueError(f"Step {idx} references column '{col}' which does not exist in the dataset.")

        # 2. Validate filtering
        if op == "filter":
            operator = step.get("operator")
            allowed_operators = {
                "equals", "not_equals", "greater_than", "less_than",
                "greater_than_or_equal", "less_than_or_equal", "contains", "in",
                "eq", "ne", "gt", "lt", "gte", "lte", "==", "!=", ">", "<", ">=", "<="
            }
            if not operator:
                raise ValueError(f"Filter step {idx} is missing the 'operator' field.")
            if operator not in allowed_operators:
                raise ValueError(f"Filter step {idx} contains unsupported operator: '{operator}'")
            if "column" not in step:
                raise ValueError(f"Filter step {idx} is missing the 'column' field.")
            if "value" not in step:
                raise ValueError(f"Filter step {idx} is missing the 'value' field.")

        # 3. Validate sorting
        if op == "sort":
            if "column" not in step:
                raise ValueError(f"Sort step {idx} is missing the 'column' field.")
            order = step.get("order")
            if order and order not in ("ascending", "descending"):
                raise ValueError(f"Sort step {idx} contains invalid order: '{order}'. Must be 'ascending' or 'descending'.")

        # 4. Validate groupby and aggregations
        if op in ("groupby", "group_by"):
            if "group" not in step:
                raise ValueError(f"Groupby step {idx} is missing the 'group' field.")
            if "target" not in step:
                raise ValueError(f"Groupby step {idx} is missing the 'target' field.")
            agg = step.get("aggregation")
            if not agg:
                raise ValueError(f"Groupby step {idx} is missing the 'aggregation' field.")
            allowed_aggs = {"mean", "median", "sum", "min", "max", "count", "n"}
            if agg not in allowed_aggs:
                raise ValueError(f"Groupby step {idx} contains unsupported aggregation: '{agg}'")

        # 5. Validate limits/head/tail
        if op in ("head", "tail", "limit"):
            limit = step.get("limit") or step.get("value")
            if limit is not None:
                try:
                    int(limit)
                except ValueError:
                    raise ValueError(f"Step {idx} contains invalid limit value: '{limit}'. Must be an integer.")
