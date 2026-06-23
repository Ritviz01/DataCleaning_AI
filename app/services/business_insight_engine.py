import polars as pl

def classify_dataset(df: pl.DataFrame) -> str:
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

def generate_business_context(df: pl.DataFrame, schema: list) -> dict:
    col_names = [col.lower().strip() for col in df.columns]
    
    # Run dataset classification
    dataset_type = classify_dataset(df)
    
    business_context = ""
    recommended_kpis = []
    
    # Checks for numeric indicators
    has_revenue = any(c in col_names for c in ["revenue", "profit", "sales", "income", "sale"])
    has_price = any(c in col_names for c in ["price", "amount", "cost", "fee", "salary", "payment"])
    has_age = "age" in col_names
    
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
        business_context = "This dataset lists computing hardware components, specifications, and retail values. It is ideal for computer hardware analysis and pricing optimization."
        if has_price:
            recommended_kpis.append("Average Price by Brand/Company")
            if "ram" in col_names:
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
