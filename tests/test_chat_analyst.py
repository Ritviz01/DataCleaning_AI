import polars as pl
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

from app.services.dataset_store import save_dataset, get_dataset, delete_dataset, list_datasets
from app.services.conversation_memory import conversation_memory
from app.services.query_validator import validate_plan
from app.services.query_executor import execute_plan

client = TestClient(app)

def test_dataset_store_functions():
    df = pl.DataFrame({"A": [1, 2, 3]})
    ds_id = save_dataset(df)
    assert ds_id is not None
    assert get_dataset(ds_id).equals(df)
    
    assert ds_id in list_datasets()
    
    deleted = delete_dataset(ds_id)
    assert deleted is True
    assert get_dataset(ds_id) is None
    assert ds_id not in list_datasets()

def test_conversation_memory():
    dataset_id = "test_memory_id"
    conversation_memory.clear_history(dataset_id)
    
    # Check empty history
    assert conversation_memory.get_history(dataset_id) == []
    
    # Add turn
    plan = {"steps": [{"operation": "filter", "column": "A", "operator": "equals", "value": 10}]}
    conversation_memory.add_turn(dataset_id, "Q1", "A1", plan, "Insight 1")
    
    history = conversation_memory.get_history(dataset_id)
    assert len(history) == 1
    assert history[0]["question"] == "Q1"
    assert history[0]["selected_filters"] == [{"column": "A", "operator": "equals", "value": 10}]
    assert "A" in history[0]["referenced_columns"]

def test_query_validator_valid():
    df = pl.DataFrame({"Price": [10.0, 20.0], "Company": ["HP", "Dell"]})
    plan = {
        "steps": [
            {"operation": "filter", "column": "Company", "operator": "equals", "value": "HP"},
            {"operation": "sort", "column": "Price", "order": "descending"}
        ]
    }
    # Should not raise any error
    validate_plan(plan, df)

def test_query_validator_invalid_column():
    df = pl.DataFrame({"Price": [10.0, 20.0]})
    plan = {
        "steps": [
            {"operation": "filter", "column": "NonExistent", "operator": "equals", "value": "HP"}
        ]
    }
    with pytest.raises(ValueError, match="does not exist"):
        validate_plan(plan, df)

def test_query_validator_invalid_op():
    df = pl.DataFrame({"Price": [10.0, 20.0]})
    plan = {
        "steps": [
            {"operation": "malicious_op", "column": "Price"}
        ]
    }
    with pytest.raises(ValueError, match="unsupported operation"):
        validate_plan(plan, df)

def test_query_executor_execution():
    df = pl.DataFrame({
        "Price": [100.0, 200.0, 150.0],
        "Company": ["HP", "Dell", "HP"]
    })
    
    # Plan: filter HP, sort Price descending
    plan = {
        "steps": [
            {"operation": "filter", "column": "Company", "operator": "equals", "value": "HP"},
            {"operation": "sort", "column": "Price", "order": "descending"}
        ]
    }
    res = execute_plan(plan, df)
    assert res.height == 2
    assert res["Price"].to_list() == [150.0, 100.0]

def test_ask_endpoint_success():
    df = pl.DataFrame({
        "Company": ["HP", "Dell"],
        "Price": [10, 20]
    })
    ds_id = save_dataset(df)
    
    with patch("app.services.query_engine.generate_operations") as mock_gen_ops, \
         patch("app.services.query_engine.generate_query_insights") as mock_gen_insights:
         
        mock_gen_ops.return_value = {
            "answer": "Here are the results filtered by HP.",
            "steps": [
                {"operation": "filter", "column": "Company", "operator": "equals", "value": "HP"}
            ]
        }
        mock_gen_insights.return_value = "HP offers products in this segment."
        
        response = client.post(
            "/ask",
            json={
                "dataset_id": ds_id,
                "question": "Show HP only"
            }
        )
        
        assert response.status_code == 200
        body = response.json()
        assert body["question"] == "Show HP only"
        assert body["answer"] == "Here are the results filtered by HP."
        assert body["insight"] == "HP offers products in this segment."
        assert len(body["table"]) == 1
        assert body["table"][0]["Company"] == "HP"
