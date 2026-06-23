def generate_sql_queries(schema: list[dict], dataset_type: str = "general_dataset") -> list[str]:
    col_names = [col.get("column_name") for col in schema]
    queries = []
    
    # 1. Base select query
    queries.append("SELECT * FROM data LIMIT 10")
    
    # Extract column subsets
    numeric_cols = []
    category_cols = []
    id_cols = []
    
    for col in schema:
        name = col.get("column_name")
        semantic = col.get("semantic_type", "")
        if semantic in ["PRICE", "AGE", "MEASUREMENT", "COUNT", "RATING", "DURATION"]:
            numeric_cols.append(name)
        elif semantic in ["CATEGORY", "COMPANY", "COURSE", "PERSON"]:
            category_cols.append(name)
        elif semantic == "ID":
            id_cols.append(name)
            
    # Add record counting query
    queries.append("SELECT COUNT(*) AS total_records FROM data")
    
    # Aggregate query for numeric metrics
    for n_col in numeric_cols[:2]:
        queries.append(f"SELECT AVG({n_col}) AS avg_{n_col.lower()}, MAX({n_col}) AS max_{n_col.lower()} FROM data")
        
    # Grouping distribution query
    for c_col in category_cols[:2]:
        queries.append(f"SELECT {c_col}, COUNT(*) AS frequency FROM data GROUP BY {c_col} ORDER BY frequency DESC")
        
    # Category with numeric aggregations query
    if category_cols and numeric_cols:
        queries.append(f"SELECT {category_cols[0]}, AVG({numeric_cols[0]}) AS avg_{numeric_cols[0].lower()} FROM data GROUP BY {category_cols[0]}")
        
    return queries[:5]
