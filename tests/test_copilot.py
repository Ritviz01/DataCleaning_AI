import pytest
import polars as pl
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

from app.db.session import Base
from app.services.copilot import intent_parser
from app.services.copilot import dataset_context
from app.services.copilot import prompt_builder
from app.services.copilot import pipeline_generator
from app.services.copilot import pipeline_validator
from app.services.copilot import copilot_service
from app.services.copilot.conversation_memory import copilot_memory
from app.services.dataset_store import save_dataset

client = TestClient(app)

@pytest.fixture
def test_db(monkeypatch, tmp_path):
    # Set up memory or temp db file
    db_file = tmp_path / "test_dataclean_copilot.db"
    db_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    
    # Re-bind engine for testing
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
    
    test_engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    
    test_session = scoped_session(sessionmaker(bind=test_engine))
    
    # Patch all session occurrences
    with patch("app.db.session.SessionLocal", test_session), \
         patch("app.api.copilot.get_db", lambda: test_session), \
         patch("app.routes.pipeline.get_db", lambda: test_session), \
         patch("app.services.dataset_store.SessionLocal", test_session):
        yield test_session
        
    Base.metadata.drop_all(bind=test_engine)

def test_intent_parser():
    # 1. Test ML preparation
    res = intent_parser.parse_intent("Prepare this dataset for Machine Learning")
    assert res["goal"] == "machine_learning"
    assert "normalize" in res["actions"]
    
    # 2. Test Cleaning with specific actions
    res = intent_parser.parse_intent("Remove duplicate records and fix dates")
    assert res["goal"] == "cleaning"
    assert "remove_duplicates" in res["actions"]
    assert "standardize_dates" in res["actions"]
    
    # 3. Test synonym matching
    res = intent_parser.parse_intent("Fix anomalies and clean null values")
    assert "fill_missing" in res["actions"]

def test_dataset_context():
    df = pl.DataFrame({
        "id": [1, 2, 3],
        "name": ["Ada", "Bob", "Charlie"],
        "email": ["ada@example.com", "bob@example.com", "charlie@example.com"],
        "amount": [10.5, 20.0, 15.5]
    })
    
    context = dataset_context.build_dataset_context(df)
    
    # Verify context schema and profile summaries
    assert context["row_count"] == 3
    assert context["column_count"] == 4
    assert any(col["name"] == "email" for col in context["columns"])
    assert any(col["name"] == "amount" for col in context["columns"])
    
    # Guarantee no raw rows are present
    assert "original_sample" not in context
    assert "transformed_sample" not in context
    # Only aggregated stats/summaries
    assert len(context["profile_summary"]) == 4

def test_prompt_builder():
    context = {
        "columns": [
            {"name": "id", "type": "Int64", "semantic_type": "ID"},
            {"name": "score", "type": "Float64", "semantic_type": "RATING"}
        ],
        "detected_issues": [
            {"column": "id", "issue_type": "duplicate_ids", "count": 2, "severity": "high"}
        ],
        "recommendations": [
            {"column": "id", "recommended_action": "manual_review", "reason": "duplicates"}
        ]
    }
    
    prompt = prompt_builder.build_copilot_prompt("dedup the id column", context)
    
    # Assert instructions and rules are present
    assert "dedup the id column" in prompt
    assert "remove_duplicates" in prompt
    assert "valid JSON" in prompt

def test_validator():
    df = pl.DataFrame({
        "id": [1, 2, 3],
        "amount": [10.0, 20.0, 30.0]
    })
    
    # 1. Circular Rename validation error
    pipeline_data = {
        "pipeline_name": "Bad Pipeline",
        "steps": [
            {"order": 1, "transformation": "rename_column", "params": {"column": "amount", "new_name": "cost"}},
            {"order": 2, "transformation": "rename_column", "params": {"column": "cost", "new_name": "amount"}}
        ]
    }
    res = pipeline_validator.validate_copilot_pipeline(df, pipeline_data)
    assert not res["valid"]
    assert any("Circular rename" in e["message"] for e in res["errors"])
    
    # 2. Rename to existing column validation error
    pipeline_data = {
        "pipeline_name": "Bad Pipeline 2",
        "steps": [
            {"order": 1, "transformation": "rename_column", "params": {"column": "amount", "new_name": "id"}}
        ]
    }
    res = pipeline_validator.validate_copilot_pipeline(df, pipeline_data)
    assert not res["valid"]
    assert any("already exists" in e["message"] for e in res["errors"])

def test_conversation_memory():
    session_id = "test_session_123"
    copilot_memory.clear_history(session_id)
    
    pipeline_data = {
        "pipeline_name": "Test Memory",
        "steps": [{"order": 1, "transformation": "remove_duplicates", "params": {}}]
    }
    
    copilot_memory.add_turn(session_id, "deduplicate score", "Removed duplicates", pipeline_data)
    history = copilot_memory.get_history(session_id)
    
    assert len(history) == 1
    assert history[0]["question"] == "deduplicate score"
    assert history[0]["generated_pipeline"]["pipeline_name"] == "Test Memory"
    
    # Clean memory
    copilot_memory.clear_history(session_id)
    assert len(copilot_memory.get_history(session_id)) == 0

@patch("app.services.copilot.pipeline_generator.OpenAI")
def test_pipeline_generator_openai_call(mock_openai_class):
    # Mocking OpenAI client and responses
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    # Setup mock LLM response returning JSON block
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""
        {
          "pipeline_name": "ML Preprocessing",
          "description": "ML pipeline",
          "steps": [
            {
              "operation": "remove_duplicates",
              "parameters": {}
            }
          ]
        }
        """))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    # Run generator
    res = pipeline_generator.generate_pipeline("dummy prompt")
    
    assert res["pipeline_name"] == "ML Preprocessing"
    # Ensure alternate keys 'operation'/'parameters' were correctly normalized
    assert len(res["steps"]) == 1
    assert res["steps"][0]["transformation"] == "remove_duplicates"
    assert res["steps"][0]["params"] == {}

@patch("app.services.copilot.pipeline_generator.OpenAI")
def test_copilot_service_and_api(mock_openai_class, test_db):
    # Setup mock LLM response
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="""
        {
          "pipeline_name": "AI Cleaned",
          "description": "AI cleanup description",
          "steps": [
            {
              "transformation": "remove_duplicates",
              "params": {}
            }
          ]
        }
        """))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    # 1. Save dummy dataset
    df = pl.DataFrame({
        "id": [1, 2, 2],
        "name": ["Ada", "Bob", "Bob"]
    })
    dataset_id = save_dataset(df)
    
    # 2. Test generate endpoint
    response = client.post("/copilot/generate", json={
        "dataset_id": dataset_id,
        "prompt": "clean this dataset",
        "session_id": "test_session_api"
    })
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["pipeline"]["pipeline_name"] == "AI Cleaned"
    assert res_data["validation"]["valid"] is True
    assert res_data["preview"]["changed_rows"] == 1
    
    # 3. Test run endpoint
    response = client.post("/copilot/run", json={
        "dataset_id": dataset_id,
        "pipeline_data": res_data["pipeline"]
    })
    assert response.status_code == 200
    run_res = response.json()
    assert run_res["status"] == "completed"
    assert run_res["rows_after"] == 2
    
    # 4. Test history endpoint
    response = client.get("/copilot/history?session_id=test_session_api")
    assert response.status_code == 200
    hist = response.json()
    assert len(hist["session_history"]) == 1
    assert len(hist["saved_pipelines"]) == 1
