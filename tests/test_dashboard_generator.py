import polars as pl
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

from app.services.dataset_store import save_dataset
from app.services.dashboard_domain_detector import detect_domain
from app.services.dashboard_kpi_engine import calculate_kpis, calculate_kpi_value
from app.services.dashboard_chart_engine import recommend_charts
from app.services.dashboard_layout_engine import build_layout
from app.services.dashboard_explainer import generate_explanation

client = TestClient(app)

def test_domain_detector():
    df = pl.DataFrame({
        "student_id": [1, 2, 3],
        "course": ["Math", "Science", "Math"],
        "grade": ["A", "B", "A"]
    })
    schema = [
        {"column_name": "student_id", "semantic_type": "ID", "data_type": "Int64"},
        {"column_name": "course", "semantic_type": "CATEGORY", "data_type": "String"},
        {"column_name": "grade", "semantic_type": "CATEGORY", "data_type": "String"}
    ]
    # Locally falls back or uses LLM. We check that it runs and returns a domain name.
    domain = detect_domain(df, schema)
    assert domain is not None
    assert isinstance(domain, str)

def test_kpi_engine():
    df = pl.DataFrame({
        "Price": [100.0, 200.0, 300.0],
        "Quantity": [1, 2, 3]
    })
    
    # 1. Test sum
    assert calculate_kpi_value(df, "Price", "sum") == 600.0
    # 2. Test mean
    assert calculate_kpi_value(df, "Price", "mean") == 200.0
    # 3. Test count
    assert calculate_kpi_value(df, "Quantity", "count") == 3
    # 4. Test unique count
    assert calculate_kpi_value(df, "Quantity", "unique_count") == 3
    
    # Test batch list calculation
    kpis = [
        {"name": "Total Cost", "column": "Price", "aggregation": "sum", "priority": "High"},
        {"name": "Avg Volume", "column": "Quantity", "aggregation": "mean", "priority": "Medium"}
    ]
    res = calculate_kpis(kpis, df)
    assert len(res) == 2
    assert res[0]["value"] == 600.0
    assert res[1]["value"] == 2.0

def test_chart_engine():
    schema = [
        {"column_name": "Date", "semantic_type": "DATE", "data_type": "String"},
        {"column_name": "Sales", "semantic_type": "PRICE", "data_type": "Float64"},
        {"column_name": "Category", "semantic_type": "CATEGORY", "data_type": "String"}
    ]
    charts = recommend_charts(schema, "Sales")
    assert len(charts) > 0
    # Must contain a Line Chart for Date + Sales trend
    chart_types = [c["chart_type"] for c in charts]
    assert "Line Chart" in chart_types
    assert "Bar Chart" in chart_types

def test_layout_engine():
    kpis = [{"name": "Metric A", "priority": "High"}, {"name": "Metric B", "priority": "Medium"}]
    charts = [{"title": "Chart A", "priority": "High"}, {"title": "Chart B", "priority": "Medium"}]
    
    layout = build_layout("Finance", kpis, charts)
    # Check that Overview page gets High priority metrics/charts
    overview = next(p for p in layout if p["page"] == "Overview")
    assert len(overview["kpis"]) == 1
    assert len(overview["charts"]) == 1

def test_explainer():
    spec = {
        "title": "Sales Performance",
        "pages": [
            {
                "page": "Overview",
                "kpis": [{"name": "Revenue", "column": "Sales"}],
                "charts": [
                    {
                        "title": "Revenue Over Time",
                        "x_axis": "Date",
                        "y_axis": "Sales",
                        "business_value": "Clarity on sales timeline.",
                        "insight": "Peaks indicate weekend volume."
                    }
                ]
            }
        ]
    }
    explanation = generate_explanation(spec)
    assert explanation["summary"] is not None
    assert len(explanation["details"]) == 1
    assert explanation["details"][0]["component"] == "Revenue Over Time"
    assert explanation["details"][0]["kpi_supported"] == "Revenue"

def test_dashboard_endpoint_success():
    df = pl.DataFrame({
        "Company": ["HP", "Dell"],
        "Price": [10, 20]
    })
    ds_id = save_dataset(df)
    
    with patch("app.services.dashboard_json_generator.generate_spec") as mock_gen_spec:
        mock_gen_spec.return_value = {
            "title": "Mock Laptops Dashboard",
            "pages": [
                {
                    "page": "Overview",
                    "description": "Overview specs",
                    "kpis": [{"name": "Total Listings", "column": "Company", "aggregation": "count"}],
                    "charts": [
                        {
                            "chart_type": "Bar Chart",
                            "title": "Price by Company",
                            "x_axis": "Company",
                            "y_axis": "Price",
                            "aggregation": "mean",
                            "priority": "High"
                        }
                    ]
                }
            ]
        }
        
        response = client.post(
            "/datasets/dashboard",
            json={
                "dataset_id": ds_id
            }
        )
        
        assert response.status_code == 200
        body = response.json()
        assert body["dataset_id"] == ds_id
        assert body["title"] == "Mock Laptops Dashboard"
        assert body["specification"]["dashboard"]["pages"][0]["kpis"][0]["value"] == 2.0
