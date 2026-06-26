from typing import Any, Dict, List

def recommend_charts(schema: List[Dict[str, Any]], domain: str) -> List[Dict[str, Any]]:
    """Suggests list of relevant, valid chart specifications based on column schema.
    
    Args:
        schema: List of column metadata dictionaries.
        domain: Detected domain name.
        
    Returns:
        List of recommended chart specification dictionaries.
    """
    numeric_cols = []
    date_cols = []
    category_cols = []
    
    for col in schema:
        name = col.get("column_name")
        dtype = col.get("data_type", "")
        semantic = col.get("semantic_type", "")
        
        if semantic == "DATE" or "date" in name.lower() or "time" in name.lower():
            date_cols.append(name)
        elif semantic in ["PRICE", "AGE", "MEASUREMENT", "COUNT", "RATING", "DURATION"] or dtype in ["Int64", "Float64", "Int32", "Float32"]:
            numeric_cols.append(name)
        elif semantic in ["CATEGORY", "COMPANY"] or dtype == "String":
            category_cols.append(name)

    charts = []

    # 1. Date + Numeric -> Line Chart (High Priority)
    for d_col in date_cols:
        for n_col in numeric_cols:
            charts.append({
                "chart_type": "Line Chart",
                "title": f"{n_col} Trend over Time",
                "x_axis": d_col,
                "y_axis": n_col,
                "aggregation": "sum" if n_col.lower() in ("sales", "revenue", "profit", "amount") else "mean",
                "priority": "High",
                "reason": f"Tracks changes and growth trends of {n_col} over {d_col} timeline."
            })

    # 2. Category + Numeric -> Bar Chart / Horizontal Bar Chart (High/Medium Priority)
    for c_col in category_cols:
        for n_col in numeric_cols:
            is_high = c_col.lower() in ("category", "department", "company", "brand", "industry", "region")
            charts.append({
                "chart_type": "Bar Chart",
                "title": f"Average {n_col} by {c_col}",
                "x_axis": c_col,
                "y_axis": n_col,
                "aggregation": "mean",
                "priority": "High" if is_high else "Medium",
                "reason": f"Compares how average {n_col} differs across different {c_col} groups."
            })

    # 3. Part-to-Whole / Category breakdowns -> Pie Chart / Treemap (Medium Priority)
    for c_col in category_cols:
        charts.append({
            "chart_type": "Pie Chart",
            "title": f"{c_col} Breakdown",
            "x_axis": c_col,
            "y_axis": c_col,
            "aggregation": "count",
            "priority": "Medium",
            "reason": f"Visualizes the volume distribution across {c_col} categories."
        })
        if len(category_cols) > 1:
            charts.append({
                "chart_type": "Treemap",
                "title": f"{c_col} Hierarchy Breakdown",
                "x_axis": c_col,
                "y_axis": c_col,
                "aggregation": "count",
                "priority": "Medium",
                "reason": f"Displays hierarchical proportions of {c_col} segments."
            })

    # 4. Numeric -> Histogram (Medium Priority)
    for n_col in numeric_cols:
        charts.append({
            "chart_type": "Histogram",
            "title": f"{n_col} Distribution",
            "x_axis": n_col,
            "y_axis": "Frequency",
            "aggregation": "count",
            "priority": "Medium",
            "reason": f"Shows the visual spread and outliers for {n_col} values."
        })

    # 5. Outliers -> Box Plot (Low Priority)
    for n_col in numeric_cols:
        charts.append({
            "chart_type": "Box Plot",
            "title": f"{n_col} Outliers & Range",
            "x_axis": None,
            "y_axis": n_col,
            "aggregation": "identity",
            "priority": "Low",
            "reason": f"Identifies outliers, median, and quartiles for {n_col} across the dataset."
        })

    # 6. Correlation -> Scatter Plot (Low Priority)
    if len(numeric_cols) >= 2:
        for i in range(min(len(numeric_cols) - 1, 3)):
            charts.append({
                "chart_type": "Scatter Plot",
                "title": f"{numeric_cols[i]} vs {numeric_cols[i+1]} Correlation",
                "x_axis": numeric_cols[i],
                "y_axis": numeric_cols[i+1],
                "aggregation": "identity",
                "priority": "Low",
                "reason": f"Analyzes relationships and clustering between {numeric_cols[i]} and {numeric_cols[i+1]}."
            })

    # Return top recommendations sorted by priority (High first, then Medium, then Low)
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    charts.sort(key=lambda c: priority_order.get(c["priority"], 3))
    return charts
