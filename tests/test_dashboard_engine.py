import pytest
import polars as pl
from fastapi.testclient import TestClient
from main import app
from app.services.dataset_store import save_dataset
from app.services.dashboard_service import generate_dashboard, get_dashboard_from_db, save_dashboard_to_db
from app.db.session import SessionLocal
from app.models.dashboard import Dashboard

client = TestClient(app)

def test_generate_dashboard_elements():
    df = pl.DataFrame({
        "student_id": ["STU001", "STU002", "STU003"],
        "age": [20, 22, 21],
        "grade_gpa": [3.6, 3.8, 3.2],
        "course_name": ["Math", "Science", "Math"],
        "enroll_date": ["2026-01-01", "2026-01-02", "2026-01-03"]
    })
    
    schema = [
        {"column_name": "student_id", "semantic_type": "ID", "data_type": "String"},
        {"column_name": "age", "semantic_type": "AGE", "data_type": "Int64"},
        {"column_name": "grade_gpa", "semantic_type": "RATING", "data_type": "Float64"},
        {"column_name": "course_name", "semantic_type": "CATEGORY", "data_type": "String"},
        {"column_name": "enroll_date", "semantic_type": "DATE", "data_type": "String"}
    ]
    
    # Generate dashboard specification
    spec = generate_dashboard(df, schema, {}, {})
    
    assert "dashboard" in spec
    assert "title" in spec["dashboard"]
    assert len(spec["dashboard"]["pages"]) > 0
    
    # Assert pages and layouts exist
    pages = spec["dashboard"]["pages"]
    page_names = [p["page"] for p in pages]
    assert "Overview" in page_names
    assert "Student Profiles" in page_names or "Demographics" in page_names or "Overview" in page_names
    
    # Verify KPIs and charts are generated and categorized
    kpis_total = sum(len(p.get("kpis", [])) for p in pages)
    charts_total = sum(len(p.get("charts", [])) for p in pages)
    
    assert kpis_total > 0
    assert charts_total > 0

def test_dashboard_persistence_and_apis():
    df = pl.DataFrame({
        "Price": [10.0, 20.0, 30.0],
        "Quantity": [5, 10, 15]
    })
    ds_id = save_dataset(df)
    
    # 1. Verify GET /dashboard/{dataset_id} generates and stores on demand if it doesn't exist
    response = client.get(f"/datasets/dashboard/{ds_id}")
    assert response.status_code == 200
    body = response.json()
    assert "dashboard" in body
    assert "title" in body["dashboard"]
    
    # Check DB persistence
    db_json = get_dashboard_from_db(ds_id)
    assert db_json is not None
    assert db_json["dashboard"]["title"] == body["dashboard"]["title"]
    
    # 2. Verify POST /dashboard/{dataset_id}/generate regenerates the dashboard
    post_response = client.post(f"/datasets/dashboard/{ds_id}/generate")
    assert post_response.status_code == 200
    post_body = post_response.json()
    assert "dashboard" in post_body
    
    # Verify updated DB content matches
    db_json_after = get_dashboard_from_db(ds_id)
    assert db_json_after is not None
    assert db_json_after["dashboard"]["title"] == post_body["dashboard"]["title"]

def test_dashboard_api_not_found():
    response = client.get("/datasets/dashboard/non_existent_id")
    assert response.status_code == 404
    
    post_response = client.post("/datasets/dashboard/non_existent_id/generate")
    assert post_response.status_code == 404
