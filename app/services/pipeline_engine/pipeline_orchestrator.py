import uuid
import json
import time
import polars as pl
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, Tuple

from app.models.pipeline import Pipeline, PipelineStep, PipelineRun
from app.services.pipeline_engine.transformation_registry import registry
from app.services.pipeline_engine.transformation_executor import execute_step
from app.services.pipeline_engine.pipeline_validator import validate_pipeline
from app.services.pipeline_engine.preview_engine import preview_pipeline_execution
from app.services.pipeline_engine import pipeline_history
from app.services.pipeline_engine.pipeline_templates import get_template_steps
from app.services.dataset_store import dataset_store
from app.services.schema_engine import infer_schema

def create_pipeline(
    db: Session,
    name: str,
    description: Optional[str] = None,
    dataset_id: Optional[str] = None,
    stop_on_error: bool = True
) -> Pipeline:
    pipeline_id = str(uuid.uuid4())
    db_pipeline = Pipeline(
        id=pipeline_id,
        name=name,
        description=description,
        dataset_id=dataset_id,
        stop_on_error=stop_on_error
    )
    db.add(db_pipeline)
    db.commit()
    db.refresh(db_pipeline)
    return db_pipeline

def get_pipeline(db: Session, pipeline_id: str) -> Optional[Pipeline]:
    return db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

def list_pipelines(db: Session) -> List[Pipeline]:
    return db.query(Pipeline).all()

def add_step(
    db: Session,
    pipeline_id: str,
    transformation: str,
    params: Dict[str, Any],
    order: Optional[int] = None
) -> Optional[PipelineStep]:
    # Check if pipeline exists
    pipeline = get_pipeline(db, pipeline_id)
    if not pipeline:
        return None
        
    # Get current steps count
    existing_steps = db.query(PipelineStep).filter(PipelineStep.pipeline_id == pipeline_id).all()
    if order is None:
        order = len(existing_steps) + 1
        
    step_id = str(uuid.uuid4())
    db_step = PipelineStep(
        id=step_id,
        pipeline_id=pipeline_id,
        order=order,
        transformation=transformation,
        params=json.dumps(params) if params else "{}"
    )
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    return db_step

def remove_step(db: Session, pipeline_id: str, step_id: str) -> bool:
    db_step = db.query(PipelineStep).filter(
        PipelineStep.pipeline_id == pipeline_id, 
        PipelineStep.id == step_id
    ).first()
    
    if not db_step:
        return False
        
    db.delete(db_step)
    db.commit()
    
    # Re-order remaining steps
    remaining_steps = db.query(PipelineStep).filter(
        PipelineStep.pipeline_id == pipeline_id
    ).order_by(PipelineStep.order).all()
    
    for idx, step in enumerate(remaining_steps):
        step.order = idx + 1
        
    db.commit()
    return True

def reorder_steps(db: Session, pipeline_id: str, step_orders: List[Dict[str, Any]]) -> bool:
    """
    step_orders list format: [{"step_id": "uuid", "order": 1}, ...]
    """
    pipeline = get_pipeline(db, pipeline_id)
    if not pipeline:
        return False
        
    # Build maps of steps for validation
    db_steps = {s.id: s for s in db.query(PipelineStep).filter(PipelineStep.pipeline_id == pipeline_id).all()}
    
    for s_order in step_orders:
        s_id = s_order.get("step_id")
        new_order = s_order.get("order")
        if s_id in db_steps and new_order is not None:
            db_steps[s_id].order = new_order
            
    db.commit()
    return True

def apply_template(db: Session, pipeline_id: str, template_name: str, dataset_id: Optional[str] = None) -> bool:
    pipeline = get_pipeline(db, pipeline_id)
    if not pipeline:
        return False
        
    # Delete existing steps first
    db.query(PipelineStep).filter(PipelineStep.pipeline_id == pipeline_id).delete()
    db.commit()
    
    # Try to infer schema if dataset_id is provided
    schema = None
    if dataset_id:
        df = dataset_store.get(dataset_id)
        if df is not None:
            schema = infer_schema(df)
            
    steps = get_template_steps(template_name, schema)
    
    for idx, step in enumerate(steps):
        add_step(
            db=db,
            pipeline_id=pipeline_id,
            transformation=step["transformation"],
            params=step["params"],
            order=idx + 1
        )
        
    return True

def run_pipeline(db: Session, pipeline_id: str, dataset_id: str) -> Optional[Dict[str, Any]]:
    pipeline = get_pipeline(db, pipeline_id)
    if not pipeline:
        return None
        
    stop_on_error = pipeline.stop_on_error
        
    # Load dataset
    df = dataset_store.get(dataset_id)
    if df is None:
        raise ValueError(f"Dataset '{dataset_id}' not found.")
        
    # Fetch steps
    steps = db.query(PipelineStep).filter(PipelineStep.pipeline_id == pipeline_id).order_by(PipelineStep.order).all()
    steps_list = [
        {
            "order": s.order,
            "transformation": s.transformation,
            "params": json.loads(s.params) if s.params else {}
        }
        for s in steps
    ]
    
    # Validate before running
    is_valid, errors, _ = validate_pipeline(df, steps_list)
    if not is_valid:
        raise ValueError(f"Pipeline validation failed: {json.dumps(errors)}")
        
    # Create execution record
    db_run = pipeline_history.create_run(db, pipeline_id, dataset_id, df.height)
    run_id = db_run.id
    
    current_df = df.clone()
    steps_executed = 0
    steps_failed = 0
    failed_logs = []
    
    overall_columns_modified = set()
    
    for step in steps_list:
        transformation = step["transformation"]
        params = step["params"]
        order = step["order"]
        
        # Run step
        updated_df, step_res = execute_step(current_df, transformation, params)
        
        # Log to db
        pipeline_history.create_step_log(
            db=db,
            run_id=run_id,
            step_order=order,
            transformation=transformation,
            status=step_res.status,
            started_at_ts=step_res.started_at,
            duration_ms=step_res.duration_ms,
            rows_affected=step_res.rows_affected,
            columns_affected=step_res.columns_affected,
            error_message=step_res.error_message,
            details=step_res.details
        )
        
        if step_res.status == "success":
            current_df = updated_df
            steps_executed += 1
            overall_columns_modified.update(step_res.columns_affected)
        else:
            steps_failed += 1
            failed_logs.append(step_res.error_message)
            
            if stop_on_error:
                # Halt execution
                pipeline_history.update_run_failed(
                    db=db,
                    run_id=run_id,
                    steps_executed=steps_executed,
                    steps_failed=steps_failed,
                    error_summary=json.dumps(failed_logs)
                )
                return pipeline_history.get_run(db, run_id)
                
    # Update run record
    if steps_failed == 0:
        pipeline_history.update_run_success(
            db=db,
            run_id=run_id,
            rows_after=current_df.height,
            columns_modified=len(overall_columns_modified),
            steps_executed=steps_executed
        )
    else:
        pipeline_history.update_run_partial(
            db=db,
            run_id=run_id,
            rows_after=current_df.height,
            columns_modified=len(overall_columns_modified),
            steps_executed=steps_executed,
            steps_failed=steps_failed,
            error_summary=json.dumps(failed_logs)
        )
        
    # Store the output dataset
    # We prefix dataset versioning status
    new_dataset_id = dataset_store.store(
        dataframe=current_df,
        status="pipeline_cleaned",
        quality_score=None # analysis can recompute quality score later
    )
    
    # Store intermediate info or links in run details/history
    # Update database run dataset_id to the new one if needed, or keep original.
    # The specification says: store dataset id used, and rows_after. We keep the run links!
    # Let's return details
    res_details = pipeline_history.get_run(db, run_id)
    res_details["output_dataset_id"] = new_dataset_id
    return res_details
