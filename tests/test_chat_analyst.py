import io
import polars as pl
import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.dataset_store import dataset_store
from app.services.query_executor import execute_query
from unittest.mock import patch

client = TestClient(app)

def test_dataset_store():
    df = pl.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
    dataset_id = dataset_store.store(df)
    assert dataset_id is not None
    assert len(dataset_id) == 12
    
    retrieved = dataset_store.get(dataset_id)
    assert retrieved is not None
    assert retrieved.equals(df)

def test_query_executor_success():
    df = pl.DataFrame({
        "Price": [10.0, 20.0, 30.0],
        "Company": ["A", "B", "A"]
    })
    
    # 1. Simple head
    res = execute_query('df.head(2)', df)
    assert res["success"] is True
    assert len(res["result"]) == 2
    
    # 2. Sort descending
    res = execute_query('df.sort("Price", descending=True).head(1)', df)
    assert res["success"] is True
    assert res["result"][0]["Price"] == 30.0
    
    # 3. Group by and aggregation
    res = execute_query('df.group_by("Company").agg(pl.col("Price").mean()).sort("Company")', df)
    assert res["success"] is True
    assert res["result"][0]["Company"] == "A"
    assert res["result"][0]["Price"] == 20.0 # (10 + 30)/2 = 20

def test_query_executor_unsafe_operations():
    df = pl.DataFrame({"Price": [10, 20]})
    
    # 1. Block imports
    res = execute_query('__import__("os").system("echo 1")', df)
    assert res["success"] is False
    assert "Blocked" in res["error"]
    
    # 2. Block file access
    res = execute_query('open("test.txt")', df)
    assert res["success"] is False
    assert "Blocked" in res["error"]
    
    # 3. Block private attributes
    res = execute_query('df.__class__.__base__', df)
    assert res["success"] is False
    assert "Blocked" in res["error"]
    
    # 4. Block unauthorized variables
    res = execute_query('import_module', df)
    assert res["success"] is False
    assert "Blocked" in res["error"]

def test_query_executor_invalid_columns():
    df = pl.DataFrame({"Price": [10, 20]})
    
    res = execute_query('df.select("NonExistentColumn")', df)
    assert res["success"] is False
    assert "does not exist" in res["error"]
    
    res = execute_query('df.filter(pl.col("NonExistentColumn") > 10)', df)
    assert res["success"] is False
    assert "does not exist" in res["error"]

def test_upload_endpoints_return_dataset_id():
    csv_data = "Company,Price\nGoogle,100\nApple,150\n"
    
    # 1. Analyze endpoint
    response = client.post(
        "/datasets/analyze",
        files={"file": ("laptops.csv", csv_data.encode(), "text/csv")}
    )
    assert response.status_code == 200
    body = response.json()
    assert "dataset_id" in body
    dataset_id = body["dataset_id"]
    assert dataset_id is not None
    
    # Retrieve from dataset store
    df = dataset_store.get(dataset_id)
    assert df is not None
    assert df.height == 2
    assert "Company" in df.columns

def test_ask_endpoint_success():
    df = pl.DataFrame({
        "Company": ["A", "B"],
        "Price": [10, 20]
    })
    dataset_id = dataset_store.store(df)
    
    with patch("app.routes.analysis.generate_query_plan") as mock_gen_plan, \
         patch("app.routes.analysis.generate_query_insights") as mock_gen_insights:
         
        mock_gen_plan.return_value = {
            "polars_code": 'df.sort("Price", descending=True).head(1)',
            "explanation": "Sorted by Price descending and took the first record",
            "required_columns": ["Price"]
        }
        mock_gen_insights.return_value = "Company B has the highest Price, indicating premium positioning."
        
        response = client.post(
            "/ask",
            json={
                "dataset_id": dataset_id,
                "question": "Show the company with the highest price"
            }
        )
        
        assert response.status_code == 200
        body = response.json()
        assert body["question"] == "Show the company with the highest price"
        assert "Sorted by Price descending" in body["answer"]
        assert "Company B has the highest Price" in body["answer"]
        assert len(body["data"]) == 1
        assert body["data"][0]["Company"] == "B"
        assert body["data"][0]["Price"] == 20
