import polars as pl
from fastapi.testclient import TestClient
from main import app

from app.services.dataset_classifier import classify_dataset_locally
from app.services.kpi_generator import generate_kpis
from app.services.chart_recommender import recommend_charts
from app.services.human_review_engine import generate_review_flags
from app.services.data_dictionary import generate_dictionary_locally
from app.services.sql_generator import generate_sql_queries
from app.services.report_generator import generate_report_locally

client = TestClient(app)

def test_classifier_heuristics():
    res = classify_dataset_locally(["student_id", "course", "grade"])
    assert res["dataset_type"] == "Education"
    assert res["confidence"] == 0.90
    
    res = classify_dataset_locally(["employee_id", "attrition", "salary"])
    assert res["dataset_type"] == "HR"
    
    res = classify_dataset_locally(["product_id", "price", "order_id"])
    assert res["dataset_type"] == "Ecommerce"

def test_kpi_generator():
    schema = [{"column_name": "student_id"}, {"column_name": "gpa"}]
    kpis = generate_kpis("Education", schema)
    assert "Average Course Rating" in kpis
    assert "Average Grade / GPA" in kpis

    schema_hr = [{"column_name": "employee_id"}, {"column_name": "salary"}]
    kpis_hr = generate_kpis("HR", schema_hr)
    assert "Employee Count" in kpis_hr
    assert "Average Salary" in kpis_hr

def test_chart_recommender():
    schema = [
        {"column_name": "date_col", "semantic_type": "DATE", "data_type": "String"},
        {"column_name": "sales_col", "semantic_type": "PRICE", "data_type": "Float64"},
        {"column_name": "category_col", "semantic_type": "CATEGORY", "data_type": "String"}
    ]
    recs = recommend_charts(schema)
    charts = [r["chart"] for r in recs]
    assert "Line Chart" in charts
    assert "Bar Chart" in charts
    assert "Histogram" in charts
    assert "Pie Chart" in charts

def test_human_review_engine():
    issues = [
        {"column": "course_id", "issue_type": "duplicate_ids", "count": 10},
        {"column": "price", "issue_type": "outliers", "count": 25}
    ]
    flags = generate_review_flags(issues, [])
    reasons = [f["reason"] for f in flags]
    assert any("duplicate ids" in r for r in reasons)
    assert any("suspicious outliers" in r for r in reasons)

def test_data_dictionary():
    schema = [
        {"column_name": "price", "semantic_type": "PRICE", "data_type": "Float64"},
        {"column_name": "student_id", "semantic_type": "ID", "data_type": "String"}
    ]
    doc = generate_dictionary_locally(schema)
    assert "selling price" in doc["price"]["description"]
    assert "identifier" in doc["student_id"]["description"]

def test_sql_generator():
    schema = [
        {"column_name": "category", "semantic_type": "CATEGORY", "data_type": "String"},
        {"column_name": "revenue", "semantic_type": "PRICE", "data_type": "Float64"}
    ]
    queries = generate_sql_queries(schema)
    assert any("COUNT(*)" in q for q in queries)
    assert any("AVG(" in q for q in queries)

def test_report_generator():
    metadata = {"rows": 100, "columns": 5}
    quality = {"quality_score": 95.0, "grade": "A"}
    issues = []
    kpis = ["Total Rev"]
    charts = [{"chart": "Bar Chart"}]
    
    report = generate_report_locally(metadata, quality, issues, kpis, charts, "Finance")
    assert report["executive_summary"].startswith("This executive report covers")
    assert "Finance" in report["executive_summary"]
    assert report["suggested_kpis"] == kpis
    assert "Bar Chart" in report["suggested_charts"]

def test_upload_api_enrichment():
    csv_data = "student_id,student_name,course,age,ram\n001,Alice,Math,20,8GB\n002,Bob,Science,22,16GB\n"
    response = client.post(
        "/datasets/analyze",
        files={"file": ("people.csv", csv_data.encode(), "text/csv")}
    )
    assert response.status_code == 200
    body = response.json()
    assert "dataset_type" in body
    assert "recommended_kpis" in body
    assert "recommended_charts" in body
    assert "human_review_flags" in body
    assert "data_dictionary" in body
    assert "sql_queries" in body
    assert "executive_report" in body
    
    # Check that it identifies domain correctly
    assert body["dataset_type"] == "Education"
