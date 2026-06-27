import polars as pl

def classify_dataset(df: pl.DataFrame, domain: str = None) -> str:
    if domain and domain.lower() in ("electronics", "electronics_dataset", "laptop"):
        return "electronics_dataset"

    columns = [c.lower() for c in df.columns]

    # Reference Dataset
    if len(columns) == 1:
        return "reference_dataset"

    if "industry" in columns and len(columns) <= 2:
        return "reference_dataset"

    # Education
    if "student_id" in columns or "course" in columns:
        return "education_dataset"

    # Laptop
    if "ram" in columns and "cpu" in columns:
        return "electronics_dataset"

    return "general_dataset"

def generate_business_context(df: pl.DataFrame, schema: list, domain: str = None) -> dict:
    col_names = [col.lower().strip() for col in df.columns]
    
    # Run dataset classification
    dataset_type = classify_dataset(df, domain=domain)
    
    business_context = ""
    recommended_kpis = []
    
    # Checks for numeric indicators
    has_revenue = any(c in col_names for c in ["revenue", "profit", "sales", "income", "sale"])
    has_price = any(c in col_names for c in ["price", "amount", "cost", "fee", "salary", "payment"])
    has_age = "age" in col_names
    
    # Helper to find column by keywords
    def find_col(keywords):
        for col in df.columns:
            if any(kw in col.lower().strip() for kw in keywords):
                return col
        return None
    
    if dataset_type == "reference_dataset":
        business_context = "Reference dataset containing lookup classifications."
        # For reference dataset, we return categories distribution KPIs
        recommended_kpis = [
            "Industry Count",
            "Industry Coverage",
            "Category Distribution"
        ]
            
    elif dataset_type == "education_dataset":
        business_context = "This dataset tracks student registration profiles, enrollment status, and academic attributes. It is designed to analyze student demographics and registration patterns."
        if has_age:
            recommended_kpis.append("Average Student Age")
        if any(c in col_names for c in ["course", "subject", "enrollment"]):
            recommended_kpis.append("Course Enrollment Distribution")
        if any(c in col_names for c in ["grade", "marks", "gpa"]):
            recommended_kpis.append("Academic Performance (GPA/Grades) Trends")
        if not recommended_kpis:
            recommended_kpis.append("Student Headcount")
            
    elif dataset_type == "electronics_dataset":
        facts = []
        
        # 1. Most frequent operating system
        os_col = find_col(["opsys", "os", "operating_system", "operating system"])
        if os_col:
            try:
                os_counts = df[os_col].drop_nulls().value_counts().sort("count", descending=True)
                if os_counts.height > 0:
                    most_common_os = os_counts[0, 0]
                    facts.append(f"most frequent operating system is {most_common_os}")
            except Exception:
                pass
                
        # 2. Highest average price brand
        brand_col = find_col(["company", "brand", "manufacturer"])
        price_col = find_col(["price", "cost", "msrp"])
        if brand_col and price_col:
            try:
                df_clean = df.filter(pl.col(price_col).is_not_null())
                price_by_brand = df_clean.group_by(brand_col).agg(pl.col(price_col).cast(pl.Float64, strict=False).mean().alias("avg_price")).filter(pl.col("avg_price").is_not_null())
                if price_by_brand.height > 0:
                    sorted_brands = price_by_brand.sort("avg_price", descending=True)
                    highest_avg_brand = sorted_brands[0, brand_col]
                    highest_avg_val = sorted_brands[0, "avg_price"]
                    facts.append(f"highest average price brand is {highest_avg_brand} (average price of {highest_avg_val:.2f})")
            except Exception:
                pass
                
        # 3. SSD vs HDD prevalence
        storage_col = find_col(["storage", "memory"])
        ram_col = find_col(["ram"])
        if storage_col and storage_col == ram_col:
            storage_col = next((c for c in df.columns if "storage" in c.lower() or ("memory" in c.lower() and "ram" not in c.lower())), None)
            
        if storage_col:
            try:
                storage_series = df[storage_col].drop_nulls().cast(pl.Utf8)
                ssd_count = storage_series.str.contains("(?i)ssd").sum()
                hdd_count = storage_series.str.contains("(?i)hdd").sum()
                if ssd_count > 0 or hdd_count > 0:
                    prev = "SSD" if ssd_count >= hdd_count else "HDD"
                    facts.append(f"{prev} storage is more prevalent (SSD: {ssd_count}, HDD: {hdd_count})")
            except Exception:
                pass
                
        facts_str = ", ".join(facts)
        if facts_str:
            business_context = f"This dataset lists computing hardware components, specifications, and retail values. Hardware analysis shows: {facts_str}. It is ideal for computer hardware analysis and pricing optimization."
        else:
            business_context = "This dataset lists computing hardware components, specifications, and retail values. It is ideal for computer hardware analysis and pricing optimization."
            
        if has_price:
            recommended_kpis.append("Average Price by Brand/Company")
            if ram_col:
                recommended_kpis.append("Price per Gigabyte of RAM")
        if any(c in col_names for c in ["cpu", "gpu"]):
            recommended_kpis.append("Market Distribution of CPU/GPU Brands")
        if not recommended_kpis:
            recommended_kpis.append("Model Count by Brand")
            
    else:  # general_dataset
        business_context = "This dataset records transaction data, product categories, and purchasing metrics. It is suitable for order fulfillment and catalog management."
        if has_revenue:
            recommended_kpis.append("Total Sales Revenue")
        if has_price:
            recommended_kpis.append("Average Order Value (AOV)")
        if "quantity" in col_names:
            recommended_kpis.append("Units Sold per Transaction")
        if not recommended_kpis:
            recommended_kpis.append("Transaction Count")

    return {
        "dataset_type": dataset_type,
        "business_context": business_context,
        "recommended_kpis": recommended_kpis
    }
