import uuid
import json
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.pipeline import PipelineRun, PipelineExecutionLog

def create_run(
    db: Session,
    pipeline_id: str,
    dataset_id: str,
    rows_before: int
) -> PipelineRun:
    run_id = str(uuid.uuid4())
    db_run = PipelineRun(
        id=run_id,
        pipeline_id=pipeline_id,
        dataset_id=dataset_id,
        status="running",
        started_at=datetime.utcnow(),
        rows_before=rows_before,
        steps_executed=0,
        steps_failed=0
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run

def update_run_success(
    db: Session,
    run_id: str,
    rows_after: int,
    columns_modified: int,
    steps_executed: int
) -> PipelineRun:
    db_run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
    if db_run:
        now = datetime.utcnow()
        db_run.status = "completed"
        db_run.completed_at = now
        db_run.rows_after = rows_after
        db_run.columns_modified = columns_modified
        db_run.steps_executed = steps_executed
        duration = (now - db_run.started_at).total_seconds()
        db_run.duration_seconds = duration
        db.commit()
        db.refresh(db_run)
    return db_run

def update_run_failed(
    db: Session,
    run_id: str,
    steps_executed: int,
    steps_failed: int,
    error_summary: str
) -> PipelineRun:
    db_run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
    if db_run:
        now = datetime.utcnow()
        db_run.status = "failed"
        db_run.completed_at = now
        db_run.steps_executed = steps_executed
        db_run.steps_failed = steps_failed
        db_run.error_summary = error_summary
        duration = (now - db_run.started_at).total_seconds()
        db_run.duration_seconds = duration
        db.commit()
        db.refresh(db_run)
    return db_run

def update_run_partial(
    db: Session,
    run_id: str,
    rows_after: int,
    columns_modified: int,
    steps_executed: int,
    steps_failed: int,
    error_summary: str
) -> PipelineRun:
    db_run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
    if db_run:
        now = datetime.utcnow()
        db_run.status = "partial"
        db_run.completed_at = now
        db_run.rows_after = rows_after
        db_run.columns_modified = columns_modified
        db_run.steps_executed = steps_executed
        db_run.steps_failed = steps_failed
        db_run.error_summary = error_summary
        duration = (now - db_run.started_at).total_seconds()
        db_run.duration_seconds = duration
        db.commit()
        db.refresh(db_run)
    return db_run

def create_step_log(
    db: Session,
    run_id: str,
    step_order: int,
    transformation: str,
    status: str,
    started_at_ts: float,
    duration_ms: float,
    rows_affected: int,
    columns_affected: List[str],
    error_message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> PipelineExecutionLog:
    log_id = str(uuid.uuid4())
    started_at_dt = datetime.utcfromtimestamp(started_at_ts)
    
    db_log = PipelineExecutionLog(
        id=log_id,
        run_id=run_id,
        step_order=step_order,
        transformation=transformation,
        status=status,
        started_at=started_at_dt,
        duration_ms=duration_ms,
        rows_affected=rows_affected,
        columns_affected=json.dumps(columns_affected) if columns_affected else "[]",
        error_message=error_message,
        details=json.dumps(details) if details else "{}"
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_run(db: Session, run_id: str) -> Optional[Dict[str, Any]]:
    db_run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
    if not db_run:
        return None
    
    logs = db.query(PipelineExecutionLog).filter(PipelineExecutionLog.run_id == run_id).order_by(PipelineExecutionLog.step_order).all()
    
    return {
        "run_id": db_run.id,
        "pipeline_id": db_run.pipeline_id,
        "dataset_id": db_run.dataset_id,
        "status": db_run.status,
        "started_at": db_run.started_at.isoformat() if db_run.started_at else None,
        "completed_at": db_run.completed_at.isoformat() if db_run.completed_at else None,
        "duration_seconds": db_run.duration_seconds,
        "steps_executed": db_run.steps_executed,
        "steps_failed": db_run.steps_failed,
        "rows_before": db_run.rows_before,
        "rows_after": db_run.rows_after,
        "columns_modified": db_run.columns_modified,
        "error_summary": json.loads(db_run.error_summary) if db_run.error_summary else None,
        "steps": [
            {
                "step_order": log.step_order,
                "transformation": log.transformation,
                "status": log.status,
                "started_at": log.started_at.isoformat() if log.started_at else None,
                "duration_ms": log.duration_ms,
                "rows_affected": log.rows_affected,
                "columns_affected": json.loads(log.columns_affected) if log.columns_affected else [],
                "error_message": log.error_message,
                "details": json.loads(log.details) if log.details else {}
            }
            for log in logs
        ]
    }

def list_runs(
    db: Session,
    pipeline_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    query = db.query(PipelineRun)
    if pipeline_id:
        query = query.filter(PipelineRun.pipeline_id == pipeline_id)
    if dataset_id:
        query = query.filter(PipelineRun.dataset_id == dataset_id)
    
    runs = query.order_by(PipelineRun.started_at.desc()).limit(limit).all()
    
    return [
        {
            "run_id": run.id,
            "pipeline_id": run.pipeline_id,
            "dataset_id": run.dataset_id,
            "status": run.status,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "duration_seconds": run.duration_seconds,
            "steps_executed": run.steps_executed,
            "steps_failed": run.steps_failed,
            "rows_before": run.rows_before,
            "rows_after": run.rows_after,
            "columns_modified": run.columns_modified
        }
        for run in runs
    ]
