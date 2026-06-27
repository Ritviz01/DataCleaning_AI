def generate_sql_queries(schema: list[dict], dataset_type: str = "general_dataset") -> list[str]:
    col_names = [col.get("column_name") for col in schema]
    queries = []
    
    # Check if domain is Electronics
    is_electronics = (
        dataset_type.lower() in ("electronics", "electronics_dataset", "laptop")
        or any(k in [n.lower() for n in col_names] for k in ["ram", "cpu", "gpu"])
    )
    
    # Helper to find column by semantic type or name matching
    def find_col_by_semantic_or_name(semantic_types, keywords):
        for col in schema:
            name = col.get("column_name")
            sem = col.get("semantic_type", "")
            if sem in semantic_types or any(k in name.lower() for k in keywords):
                return name
        return None

    if is_electronics:
        price_col = find_col_by_semantic_or_name(["PRICE"], ["price", "cost"]) or "Price"
        company_col = find_col_by_semantic_or_name(["COMPANY"], ["company", "brand", "manufacturer"]) or "Company"
        cpu_col = find_col_by_semantic_or_name(["CPU", "HARDWARE"], ["cpu", "processor"]) or "Cpu"
        ram_col = find_col_by_semantic_or_name(["MEMORY", "HARDWARE"], ["ram", "memory"]) or "Ram"
        
        queries.append("SELECT * FROM data LIMIT 10")
        queries.append(f"SELECT * FROM data ORDER BY {price_col} DESC LIMIT 10")
        queries.append(f"SELECT {company_col}, AVG({price_col}) AS avg_price FROM data GROUP BY {company_col} ORDER BY avg_price DESC")
        queries.append(f"SELECT {cpu_col}, AVG({price_col}) AS avg_price FROM data GROUP BY {cpu_col} ORDER BY avg_price DESC")
        queries.append(f"SELECT {ram_col}, AVG({price_col}) AS avg_price FROM data GROUP BY {ram_col} ORDER BY avg_price DESC")
        return queries[:5]

    # Default queries path
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
