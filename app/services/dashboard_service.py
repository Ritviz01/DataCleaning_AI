from datetime import datetime
import polars as pl
from app.services.dataset_store import get_dataset
from app.services.pipeline import analyse_dataset
from app.services.dashboard_domain_detector import detect_domain
from app.services.dashboard_recommender import recommend_dashboard_sections
from app.services.dashboard_kpi_engine import generate_kpis, calculate_kpis
from app.services.dashboard_chart_engine import recommend_charts
from app.services.dashboard_layout_engine import build_layout
from app.services.dashboard_json_generator import generate_spec
from app.services.dashboard_explainer import generate_explanation

from app.db.session import SessionLocal
from app.models.dashboard import Dashboard

DOMAIN_TITLES = {
    "Electronics": "Laptop Product Analytics Dashboard",
    "Education": "Academic Performance & Student Analytics Dashboard",
    "HR": "Human Resources & Workforce Analytics Dashboard",
    "Finance": "Financial Performance & Expenses Dashboard",
    "Healthcare": "Healthcare Patient & Clinic Operations Dashboard",
    "Ecommerce": "E-Commerce Sales & Customer Analytics Dashboard",
    "Sales": "Sales Pipeline & Performance Dashboard",
    "CRM": "Customer Relationship Management Dashboard",
    "Marketing": "Marketing Campaign Performance Dashboard"
}

def generate_dashboard(df: pl.DataFrame, schema: list[dict], profile: dict, insights: dict) -> dict:
    """Orchestrates the dynamic generation of the dashboard specification."""
    # 1. Detect Domain
    domain = detect_domain(df, schema)
    
    # 2. Recommend Dashboard Sections (Pages)
    sections = recommend_dashboard_sections(domain, schema)
    
    # 3. Generate KPIs (using the new KPI engine)
    kpis = generate_kpis(df, schema)
    
    # 4. Recommend Charts (using the new Chart engine)
    charts = recommend_charts(df, schema, domain=domain)
    
    # 5. Build Layout (arranging KPIs and charts into pages)
    pages = build_layout(domain, kpis, charts, sections)
    
    specialized_title = DOMAIN_TITLES.get(domain, f"{domain} Analysis Dashboard")
    
    # 6. Generate JSON Specification
    spec = generate_spec(schema, domain, kpis, charts, pages)
    
    # Ensure it conforms to {"dashboard": {"title": ..., "pages": ...}}
    if "dashboard" not in spec:
        title = spec.get("title")
        if not title or title in [f"{domain} Analysis Dashboard", f"{domain} Performance Dashboard", "Dashboard"]:
            title = specialized_title
        spec = {
            "dashboard": {
                "title": title,
                "pages": spec.get("pages") or pages
            }
        }
    else:
        title = spec["dashboard"].get("title")
        if not title or title in [f"{domain} Analysis Dashboard", f"{domain} Performance Dashboard", "Dashboard"]:
            spec["dashboard"]["title"] = specialized_title
        
    # Calculate Polars values for all KPIs in each page
    pages_to_calculate = spec["dashboard"].get("pages", [])
    for page in pages_to_calculate:
        page_kpis = page.get("kpis", [])
        if page_kpis:
            calculated_kpis = calculate_kpis(page_kpis, df)
            page["kpis"] = calculated_kpis
            
    return spec

def create_dashboard(dataset_id: str) -> dict:
    """Orchestrates the entire AI Dashboard Generation process for a given dataset ID.
    
    Loads from database if already exists, otherwise generates and stores.
    """
    df = get_dataset(dataset_id)
    if df is None:
        raise ValueError(f"Dataset with ID '{dataset_id}' not found.")
        
    # Check if dashboard already exists in database
    cached_dash = get_dashboard_from_db(dataset_id)
    if cached_dash:
        spec = cached_dash
        from app.services.schema_engine import infer_schema
        from app.services.metadata_service import generate_metadata
        schema = infer_schema(df)
        metadata = generate_metadata(df)
    else:
        # 1. Analyze schema and metadata
        analysis = analyse_dataset(df)
        metadata = analysis["metadata"]
        schema = analysis["schema"]
        profile = analysis["profile"]
        insights = analysis["insights"]
        
        # 2. Generate dashboard
        spec = generate_dashboard(df, schema, profile, insights)
        
        # 3. Save to database
        save_dashboard_to_db(dataset_id, spec)

    # Generate business explanation summary
    explanation = generate_explanation(spec["dashboard"], schema, metadata)
    
    return {
        "dataset_id": dataset_id,
        "domain": spec["dashboard"]["title"].replace(" Analysis Dashboard", "").replace(" Dashboard", "").replace(" Performance Dashboard", ""),
        "title": spec["dashboard"]["title"],
        "specification": spec,
        "explanation": explanation
    }

def save_dashboard_to_db(dataset_id: str, dashboard_json: dict) -> None:
    """Persists generated dashboard spec in SQL database."""
    session = SessionLocal()
    try:
        db_dash = session.query(Dashboard).filter_by(dataset_id=dataset_id).first()
        if db_dash:
            db_dash.dashboard_json = dashboard_json
            db_dash.updated_at = datetime.utcnow()
        else:
            db_dash = Dashboard(dataset_id=dataset_id, dashboard_json=dashboard_json)
            session.add(db_dash)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving dashboard to DB: {e}")
    finally:
        session.close()

def get_dashboard_from_db(dataset_id: str) -> dict | None:
    """Fetches dashboard spec from SQL database."""
    session = SessionLocal()
    try:
        db_dash = session.query(Dashboard).filter_by(dataset_id=dataset_id).first()
        return db_dash.dashboard_json if db_dash else None
    except Exception as e:
        print(f"Error getting dashboard from DB: {e}")
        return None
    finally:
        session.close()
