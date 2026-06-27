def recommend_charts(schema: list[dict], domain: str = "General") -> list[dict]:
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
            
        # Categorize
        if semantic == "DATE" or "date" in name.lower() or "time" in name.lower():
            date_cols.append(name)
        elif semantic in ["PRICE", "AGE", "MEASUREMENT", "COUNT", "RATING", "DURATION"] or dtype in ["Int64", "Float64", "Int32", "Float32"]:
            numeric_cols.append(name)
        elif semantic in ["CATEGORY", "COMPANY"] or dtype == "String":
            category_cols.append(name)
            
    recommendations = []
    
    # Rule 0: Electronics specific templates
    if domain.lower() in ("electronics", "electronics_dataset", "laptop"):
        company_col = next((col.get("column_name") for col in schema if col.get("column_name", "").lower() in ["company", "brand"]), None)
        price_col = next((col.get("column_name") for col in schema if col.get("column_name", "").lower() in ["price", "cost"]), None)
        ram_col = next((col.get("column_name") for col in schema if col.get("column_name", "").lower() in ["ram", "memory"]), None)
        
        if company_col and price_col:
            recommendations.append({
                "chart": "Bar Chart",
                "x": company_col,
                "y": price_col,
                "description": "Average Price by Company"
            })
        if ram_col:
            recommendations.append({
                "chart": "Histogram",
                "x": ram_col,
                "y": "Frequency",
                "description": "RAM Distribution"
            })
        if ram_col and price_col:
            recommendations.append({
                "chart": "Scatter Plot",
                "x": ram_col,
                "y": price_col,
                "description": "Price vs RAM"
            })

    # Rule 1: Date + Numeric -> Line Chart
    for d_col in date_cols:
        for n_col in numeric_cols:
            recommendations.append({
                "chart": "Line Chart",
                "x": d_col,
                "y": n_col,
                "description": f"Tracks {n_col} trends over time."
            })
            
    # Rule 2: Category + Numeric -> Bar Chart
    for c_col in category_cols:
        for n_col in numeric_cols:
            recommendations.append({
                "chart": "Bar Chart",
                "x": c_col,
                "y": n_col,
                "description": f"Compares {n_col} across different {c_col} categories."
            })
            
    # Rule 3: Distribution -> Histogram
    for n_col in numeric_cols:
        recommendations.append({
            "chart": "Histogram",
            "x": n_col,
            "y": "Frequency",
            "description": f"Shows the distribution spread of {n_col}."
        })
        
    # Rule 4: Correlation -> Scatter Plot
    if len(numeric_cols) >= 2:
        for i in range(len(numeric_cols) - 1):
            recommendations.append({
                "chart": "Scatter Plot",
                "x": numeric_cols[i],
                "y": numeric_cols[i+1],
                "description": f"Analyzes correlation between {numeric_cols[i]} and {numeric_cols[i+1]}."
            })
            
    # Rule 5: Part-to-Whole -> Pie Chart
    for c_col in category_cols:
        recommendations.append({
            "chart": "Pie Chart",
            "x": c_col,
            "y": "Percentage",
            "description": f"Displays the category breakdown of {c_col}."
        })
        
    return recommendations[:10]
