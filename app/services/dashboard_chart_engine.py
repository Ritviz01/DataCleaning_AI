import polars as pl
from typing import Any, Dict, List

def recommend_charts(*args, **kwargs) -> List[Dict[str, Any]]:
    """Suggests relevant chart specifications based on column schemas.
    
    Supports:
        - recommend_charts(df, schema)
        - recommend_charts(schema, domain)
    """
    if len(args) >= 1 and isinstance(args[0], pl.DataFrame):
        df = args[0]
        schema = args[1] if len(args) > 1 else []
    else:
        schema = args[0] if len(args) >= 1 else []
        domain = args[1] if len(args) > 1 else "General"
        df = None

    domain = kwargs.get("domain", "General")
    if not domain or domain == "General":
        if len(args) > 2:
            domain = args[2]

    numeric_cols = []
    date_cols = []
    category_cols = []
    
    for col in schema:
        name = col.get("column_name")
        if not name:
            continue
        dtype = col.get("data_type", "")
        semantic = col.get("semantic_type", "")
        
        col_lower = name.lower().strip()
        # Skip index and ID columns
        if (
            semantic in ("RECORD_ID", "ID")
            or col_lower == "unnamed: 0"
            or "unnamed" in col_lower
            or col_lower in ["index", "row", "row_id", "s.no", "sl_no", "serial_number", "id"]
            or col_lower.endswith("_id")
            or col_lower.startswith("id_")
        ):
            continue
        
        if semantic == "DATE" or "date" in name.lower() or "time" in name.lower():
            date_cols.append(name)
        elif semantic in ["PRICE", "AGE", "MEASUREMENT", "COUNT", "RATING", "DURATION"] or dtype in ["Int64", "Float64", "Int32", "Float32"]:
            numeric_cols.append(name)
        elif semantic in ["CATEGORY", "COMPANY", "DEPARTMENT", "GENDER", "COUNTRY", "CITY", "STATE", "STATUS"] or dtype == "String":
            category_cols.append(name)

    charts = []

    # If domain is Electronics, add specific hardware and retail templates
    if domain.lower() in ("electronics", "electronics_dataset", "laptop"):
        company_col = None
        price_col = None
        ram_col = None
        
        for col in schema:
            col_name = col.get("column_name", "")
            col_lower = col_name.lower().strip()
            if (
                col.get("semantic_type") in ("RECORD_ID", "ID")
                or col_lower == "unnamed: 0"
                or "unnamed" in col_lower
                or col_lower in ["index", "row", "row_id", "s.no", "sl_no", "serial_number", "id"]
                or col_lower.endswith("_id")
                or col_lower.startswith("id_")
            ):
                continue
            sem = col.get("semantic_type", "")
            if sem == "COMPANY" or any(kw in col_lower for kw in ["company", "brand", "manufacturer"]):
                company_col = col_name
            elif sem == "PRICE" or any(kw in col_lower for kw in ["price", "cost", "msrp"]):
                price_col = col_name
            elif sem == "MEMORY" or any(kw in col_lower for kw in ["ram", "memory"]):
                ram_col = col_name

        if company_col and price_col:
            charts.append({
                "chart_type": "Bar Chart",
                "title": "Average Price by Company",
                "x_axis": company_col,
                "y_axis": price_col,
                "aggregation": "mean",
                "priority": "High",
                "reason": "Compares the average pricing across different computing brands/manufacturers."
            })
            
        if ram_col:
            charts.append({
                "chart_type": "Histogram",
                "title": "RAM Distribution",
                "x_axis": ram_col,
                "y_axis": "Frequency",
                "aggregation": "count",
                "priority": "High",
                "reason": "Shows the market presence and distribution of different RAM capacities."
            })
            
        if ram_col and price_col:
            charts.append({
                "chart_type": "Scatter Plot",
                "title": "Price vs RAM Correlation",
                "x_axis": ram_col,
                "y_axis": price_col,
                "aggregation": "identity",
                "priority": "High",
                "reason": "Visualizes the relationship between RAM sizes and pricing tiers."
            })

    # 1. Date + Numeric -> Line Chart
    for d_col in date_cols[:2]:
        for n_col in numeric_cols[:2]:
            charts.append({
                "chart_type": "Line Chart",
                "title": f"{n_col} Trend over {d_col}",
                "x_axis": d_col,
                "y_axis": n_col,
                "aggregation": "sum" if n_col.lower() in ("sales", "revenue", "profit", "amount") else "mean",
                "priority": "High",
                "reason": f"Tracks growth trends and variations of {n_col} over the {d_col} timeline."
            })

    # 2. Category + Numeric -> Bar Chart
    for c_col in category_cols[:2]:
        for n_col in numeric_cols[:2]:
            charts.append({
                "chart_type": "Bar Chart",
                "title": f"Average {n_col} by {c_col}",
                "x_axis": c_col,
                "y_axis": n_col,
                "aggregation": "mean",
                "priority": "High" if c_col.lower() in ("category", "department", "company") else "Medium",
                "reason": f"Compares how {n_col} averages compare across {c_col} groups."
            })

    # 3. Single Numeric -> Histogram
    for n_col in numeric_cols[:3]:
        charts.append({
            "chart_type": "Histogram",
            "title": f"{n_col} Distribution",
            "x_axis": n_col,
            "y_axis": "Frequency",
            "aggregation": "count",
            "priority": "Medium",
            "reason": f"Shows distribution shape, spread, and frequency patterns for {n_col}."
        })

    # 4. Two Numeric Columns -> Scatter Plot
    if len(numeric_cols) >= 2:
        for i in range(min(len(numeric_cols) - 1, 2)):
            charts.append({
                "chart_type": "Scatter Plot",
                "title": f"{numeric_cols[i]} vs {numeric_cols[i+1]} Correlation",
                "x_axis": numeric_cols[i],
                "y_axis": numeric_cols[i+1],
                "aggregation": "identity",
                "priority": "Low",
                "reason": f"Correlates {numeric_cols[i]} values against {numeric_cols[i+1]} to identify clusters or relationships."
            })

    # 5. Categorical Distribution -> Pie Chart
    for c_col in category_cols[:2]:
        charts.append({
            "chart_type": "Pie Chart",
            "title": f"{c_col} Breakdown",
            "x_axis": c_col,
            "y_axis": c_col,
            "aggregation": "count",
            "priority": "Medium",
            "reason": f"Highlights the share distribution across different categories in {c_col}."
        })

    # 6. Outlier Analysis -> Box Plot
    for n_col in numeric_cols[:2]:
        charts.append({
            "chart_type": "Box Plot",
            "title": f"{n_col} Outliers & Range",
            "x_axis": None,
            "y_axis": n_col,
            "aggregation": "identity",
            "priority": "Low",
            "reason": f"Visualizes the summary statistics and highlights outliers for {n_col}."
        })

    # 7. Correlation -> Heatmap
    if len(numeric_cols) >= 3:
        charts.append({
            "chart_type": "Heatmap",
            "title": "Numeric Correlation Matrix",
            "x_axis": None,
            "y_axis": None,
            "aggregation": "correlation",
            "priority": "Low",
            "reason": "Map of linear correlation coefficients to detect multicollinearity or relationships between metrics."
        })

    # Sort by priority
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    charts.sort(key=lambda c: priority_order.get(c["priority"], 3))
    
    return charts
