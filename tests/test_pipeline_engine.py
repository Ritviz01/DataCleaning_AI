import pytest
import io
import json
import yaml
import polars as pl
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

from app.db.session import Base
from app.models.pipeline import Pipeline, PipelineStep, PipelineRun, PipelineExecutionLog
from app.services.pipeline_engine import pipeline_orchestrator
from app.services.pipeline_engine import pipeline_history
from app.services.pipeline_engine import pipeline_exporter
from app.services.pipeline_engine.transformation_registry import registry
from app.services.pipeline_engine.preview_engine import preview_pipeline_execution
from app.services.dataset_store import dataset_store, save_dataset

client = TestClient(app)

@pytest.fixture
def test_db(monkeypatch, tmp_path):
    # Set up memory or temp db file
    db_file = tmp_path / "test_dataclean_pipeline.db"
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
         patch("app.routes.pipeline.get_db", lambda: test_session), \
         patch("app.services.dataset_store.SessionLocal", test_session), \
         patch("app.services.pipeline_engine.pipeline_orchestrator.dataset_store", dataset_store):
        yield test_session
        
    Base.metadata.drop_all(bind=test_engine)

def test_registry_transformations():
    df = pl.DataFrame({
        "id": [1, 2, 2, 4],
        "name": [" Ada ", "Bob", "Charlie", None],
        "score": [10.5, 20.0, 15.5, 30.0],
        "category": ["A", "B", "A", "C"]
    })
    
    # 1. remove_duplicates
    handler = registry.get("remove_duplicates")
    res = handler(df, {"subset": "id"})
    assert res.height == 3
    
    # 2. fill_missing
    handler = registry.get("fill_missing")
    res = handler(df, {"column": "name", "method": "value", "fill_value": "Unknown"})
    assert res["name"][3] == "Unknown"
    
    # 3. drop_column
    handler = registry.get("drop_column")
    res = handler(df, {"column": "category"})
    assert "category" not in res.columns
    
    # 4. rename_column
    handler = registry.get("rename_column")
    res = handler(df, {"column": "score", "new_name": "final_score"})
    assert "final_score" in res.columns
    assert "score" not in res.columns
    
    # 5. trim_whitespace
    handler = registry.get("trim_whitespace")
    res = handler(df, {"column": "name"})
    assert res["name"][0] == "Ada"

def test_pipeline_validation():
    df = pl.DataFrame({
        "id": [1, 2, 3],
        "amount": [10, 20, 30]
    })
    
    # Unknown step
    steps = [{"order": 1, "transformation": "unknown_step", "params": {}}]
    is_valid, errors, _ = pipeline_orchestrator.validate_pipeline(df, steps)
    assert not is_valid
    assert len(errors) == 1
    assert "Unknown transformation" in errors[0]["message"]
    
    # Missing required parameter 'column'
    steps = [{"order": 1, "transformation": "fill_missing", "params": {"method": "median"}}]
    is_valid, errors, _ = pipeline_orchestrator.validate_pipeline(df, steps)
    assert not is_valid
    assert any("column" in e["field"] for e in errors)
    
    # Invalid column
    steps = [{"order": 1, "transformation": "drop_column", "params": {"column": "nonexistent"}}]
    is_valid, errors, _ = pipeline_orchestrator.validate_pipeline(df, steps)
    assert not is_valid
    assert any("nonexistent" in e["message"] for e in errors)

def test_pipeline_preview():
    df = pl.DataFrame({
        "id": [1, 2, 2],
        "name": ["Ada", "Bob", "Bob"]
    })
    
    steps = [
        {"transformation": "remove_duplicates", "params": {}}
    ]
    
    preview = preview_pipeline_execution(df, steps)
    assert preview["changed_rows"] == 1
    assert preview["original_sample"] == [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Bob"}, {"id": 2, "name": "Bob"}]
    assert preview["transformed_sample"] == [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Bob"}]
    
    # Verify original df is not mutated
    assert df.height == 3

def test_orchestrator_crud_and_execution(test_db):
    pipeline = pipeline_orchestrator.create_pipeline(test_db, "ML Pipeline", "Test description")
    assert pipeline.id is not None
    assert pipeline.name == "ML Pipeline"
    pipeline_id = pipeline.id
    
    # Add steps
    step1 = pipeline_orchestrator.add_step(test_db, pipeline_id, "remove_duplicates", {})
    step2 = pipeline_orchestrator.add_step(test_db, pipeline_id, "trim_whitespace", {"column": "name"})
    
    assert step1.order == 1
    assert step2.order == 2
    
    # Reorder steps
    success = pipeline_orchestrator.reorder_steps(test_db, pipeline_id, [
        {"step_id": step1.id, "order": 2},
        {"step_id": step2.id, "order": 1}
    ])
    assert success
    
    db_steps = test_db.query(PipelineStep).filter(PipelineStep.pipeline_id == pipeline_id).order_by(PipelineStep.order).all()
    assert db_steps[0].transformation == "trim_whitespace"
    assert db_steps[1].transformation == "remove_duplicates"
    
    # Execute pipeline
    df = pl.DataFrame({
        "id": [1, 2, 2],
        "name": [" Ada ", "Bob", "Bob"]
    })
    dataset_id = save_dataset(df)
    
    run_details = pipeline_orchestrator.run_pipeline(test_db, pipeline_id, dataset_id)
    assert run_details is not None
    assert run_details["status"] == "completed"
    assert run_details["rows_before"] == 3
    assert run_details["rows_after"] == 2
    
    # Check execution DB entry
    db_run = test_db.query(PipelineRun).filter(PipelineRun.pipeline_id == pipeline_id).first()
    assert db_run is not None
    assert db_run.status == "completed"
    assert db_run.rows_after == 2
    
    # Check logs
    db_logs = test_db.query(PipelineExecutionLog).filter(PipelineExecutionLog.run_id == db_run.id).all()
    assert len(db_logs) == 2

def test_pipeline_exporter(test_db):
    pipeline = pipeline_orchestrator.create_pipeline(test_db, "Export Test")
    step = pipeline_orchestrator.add_step(test_db, pipeline.id, "remove_duplicates", {})
    
    # JSON Export
    json_data = pipeline_exporter.export_pipeline_as_json(pipeline, [step])
    assert json_data["pipeline_name"] == "Export Test"
    assert len(json_data["steps"]) == 1
    
    # YAML Export
    yaml_str = pipeline_exporter.export_pipeline_as_yaml(pipeline, [step])
    parsed_yaml = yaml.safe_load(yaml_str)
    assert parsed_yaml["pipeline_name"] == "Export Test"

def test_api_endpoints(test_db):
    # 1. Create pipeline
    response = client.post("/pipeline/create", json={
        "name": "API Test Pipeline",
        "description": "API Test Desc"
    })
    assert response.status_code == 201
    pipeline_id = response.json()["pipeline_id"]
    
    # 2. Add step
    response = client.post("/pipeline/add-step", json={
        "pipeline_id": pipeline_id,
        "transformation": "remove_duplicates",
        "params": {}
    })
    assert response.status_code == 200
    step_id = response.json()["step_id"]
    
    # 3. Apply templates
    response = client.post("/pipeline/template/apply", json={
        "pipeline_id": pipeline_id,
        "template_name": "Basic Cleaning"
    })
    assert response.status_code == 200
    
    # 4. List pipelines
    response = client.get("/pipeline/list")
    assert response.status_code == 200
    assert len(response.json()) >= 1
