from app.services.dataset_store import get_dataset
from app.services.pipeline import analyse_dataset
from app.services.dashboard_domain_detector import detect_domain
from app.services.dashboard_chart_engine import recommend_charts
from app.services.dashboard_layout_engine import build_layout
from app.services.dashboard_json_generator import generate_spec
from app.services.dashboard_kpi_engine import calculate_kpis
from app.services.dashboard_explainer import generate_explanation

def create_dashboard(dataset_id: str) -> dict:
    """Orchestrates the entire AI Dashboard Generation process.
    
    Args:
        dataset_id: Unique string ID of the stored dataset.
        
    Returns:
        Complete dashboard spec payload with title, pages, KPIs, charts, and explainer.
    """
    df = get_dataset(dataset_id)
    if df is None:
        raise ValueError(f"Dataset with ID '{dataset_id}' not found.")
        
    # 1. Analyze schema and metadata
    analysis = analyse_dataset(df)
    metadata = analysis["metadata"]
    schema = analysis["schema"]
    
    # 2. Detect Domain
    domain = detect_domain(df, schema)
    
    # 3. Generate list of local KPI candidate specifications
    numeric_cols = []
    category_cols = []
    for col in schema:
        name = col.get("column_name")
        dtype = col.get("data_type", "")
        semantic = col.get("semantic_type", "")
        if semantic in ["PRICE", "AGE", "MEASUREMENT", "COUNT", "RATING", "DURATION"] or dtype in ["Int64", "Float64", "Int32", "Float32"]:
            numeric_cols.append(name)
        elif semantic in ["CATEGORY", "COMPANY"] or dtype == "String":
            category_cols.append(name)
            
    local_kpis = []
    for col in numeric_cols:
        local_kpis.append({
            "name": f"Total {col}",
            "column": col,
            "aggregation": "sum",
            "priority": "High"
        })
        local_kpis.append({
            "name": f"Average {col}",
            "column": col,
            "aggregation": "mean",
            "priority": "High"
        })
    for col in category_cols[:2]:
        local_kpis.append({
            "name": f"Unique {col} Count",
            "column": col,
            "aggregation": "unique_count",
            "priority": "Medium"
        })
    if not local_kpis:
        local_kpis.append({
            "name": "Total Records",
            "column": df.columns[0],
            "aggregation": "count",
            "priority": "High"
        })

    # 4. Generate local chart recommendations
    local_charts = recommend_charts(schema, domain)
    
    # 5. Build a default layout
    default_pages = build_layout(domain, local_kpis, local_charts)
    
    # 6. Call LLM JSON Generator to synthesize custom dashboard specification
    spec = generate_spec(schema, domain, local_kpis, local_charts, default_pages)
    
    # Ensure title is present
    if "title" not in spec:
        spec["title"] = f"{domain} Analysis Dashboard"
        
    # 7. Calculate Polars values for all KPIs in each page
    pages = spec.get("pages", [])
    for page in pages:
        page_kpis = page.get("kpis", [])
        if page_kpis:
            calculated_kpis = calculate_kpis(page_kpis, df)
            page["kpis"] = calculated_kpis
            
    # 8. Generate business explanation summary
    explanation = generate_explanation(spec)
    
    return {
        "dataset_id": dataset_id,
        "domain": domain,
        "title": spec["title"],
        "specification": {
            "dashboard": spec
        },
        "explanation": explanation
    }
