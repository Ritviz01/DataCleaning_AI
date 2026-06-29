from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.services.pipeline_engine import pipeline_orchestrator
from app.services.pipeline_engine import pipeline_history
from app.services.pipeline_engine import pipeline_exporter
from app.services.pipeline_engine.pipeline_validator import validate_pipeline
from app.services.pipeline_engine.pipeline_templates import get_available_templates
from app.services.dataset_store import dataset_store

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

# ==========================================
# Pydantic Schemas
# ==========================================

class PipelineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    dataset_id: Optional[str] = None
    stop_on_error: Optional[bool] = True

class PipelineStepAdd(BaseModel):
    pipeline_id: str
    transformation: str
    params: Dict[str, Any] = Field(default_factory=dict)
    order: Optional[int] = None

class PipelineStepRemove(BaseModel):
    pipeline_id: str
    step_id: str

class StepOrder(BaseModel):
    step_id: str
    order: int

class PipelineReorder(BaseModel):
    pipeline_id: str
    steps: List[StepOrder]

class PipelineValidate(BaseModel):
    pipeline_id: str
    dataset_id: str

class PipelinePreview(BaseModel):
    pipeline_id: str
    dataset_id: str

class PipelineRun(BaseModel):
    pipeline_id: str
    dataset_id: str

class ApplyTemplate(BaseModel):
    pipeline_id: str
    template_name: str
    dataset_id: Optional[str] = None

class PipelineExport(BaseModel):
    pipeline_id: Optional[str] = None
    run_id: Optional[str] = None
    format: str = Field(..., description="json, yaml, template, execution_report, audit_report")

# ==========================================
# Endpoints
# ==========================================

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_pipeline_endpoint(data: PipelineCreate, db: Session = Depends(get_db)):
    pipeline = pipeline_orchestrator.create_pipeline(
        db=db,
        name=data.name,
        description=data.description,
        dataset_id=data.dataset_id,
        stop_on_error=data.stop_on_error
    )
    return {
        "message": "Pipeline created successfully",
        "pipeline_id": pipeline.id,
        "name": pipeline.name
    }

@router.post("/add-step")
def add_step_endpoint(data: PipelineStepAdd, db: Session = Depends(get_db)):
    step = pipeline_orchestrator.add_step(
        db=db,
        pipeline_id=data.pipeline_id,
        transformation=data.transformation,
        params=data.params,
        order=data.order
    )
    if not step:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {
        "message": "Step added successfully",
        "step_id": step.id,
        "order": step.order
    }

@router.post("/remove-step")
def remove_step_endpoint(data: PipelineStepRemove, db: Session = Depends(get_db)):
    success = pipeline_orchestrator.remove_step(
        db=db,
        pipeline_id=data.pipeline_id,
        step_id=data.step_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Step not found in this pipeline")
    return {"message": "Step removed and pipeline reordered successfully"}

@router.post("/reorder")
def reorder_endpoint(data: PipelineReorder, db: Session = Depends(get_db)):
    success = pipeline_orchestrator.reorder_steps(
        db=db,
        pipeline_id=data.pipeline_id,
        step_orders=[s.dict() for s in data.steps]
    )
    if not success:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"message": "Steps reordered successfully"}

@router.get("/list")
def list_pipelines_endpoint(db: Session = Depends(get_db)):
    pipelines = pipeline_orchestrator.list_pipelines(db)
    return [
        {
            "pipeline_id": p.id,
            "name": p.name,
            "description": p.description,
            "dataset_id": p.dataset_id,
            "stop_on_error": p.stop_on_error,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in pipelines
    ]

@router.get("/{id}")
def get_pipeline_endpoint(id: str, db: Session = Depends(get_db)):
    pipeline = pipeline_orchestrator.get_pipeline(db, id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    # Query steps
    from app.models.pipeline import PipelineStep
    steps = db.query(PipelineStep).filter(PipelineStep.pipeline_id == id).order_by(PipelineStep.order).all()
    
    import json
    return {
        "pipeline_id": pipeline.id,
        "name": pipeline.name,
        "description": pipeline.description,
        "dataset_id": pipeline.dataset_id,
        "stop_on_error": pipeline.stop_on_error,
        "created_at": pipeline.created_at.isoformat() if pipeline.created_at else None,
        "steps": [
            {
                "step_id": s.id,
                "order": s.order,
                "transformation": s.transformation,
                "params": json.loads(s.params) if s.params else {}
            }
            for s in steps
        ]
    }

@router.post("/validate")
def validate_endpoint(data: PipelineValidate, db: Session = Depends(get_db)):
    pipeline = pipeline_orchestrator.get_pipeline(db, data.pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
        
    df = dataset_store.get(data.dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    # Get steps
    from app.models.pipeline import PipelineStep
    steps = db.query(PipelineStep).filter(PipelineStep.pipeline_id == data.pipeline_id).order_by(PipelineStep.order).all()
    import json
    steps_list = [
        {
            "order": s.order,
            "transformation": s.transformation,
            "params": json.loads(s.params) if s.params else {}
        }
        for s in steps
    ]
    
    is_valid, errors, warnings = validate_pipeline(df, steps_list)
    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings
    }

@router.post("/preview")
def preview_endpoint(data: PipelinePreview, db: Session = Depends(get_db)):
    pipeline = pipeline_orchestrator.get_pipeline(db, data.pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
        
    df = dataset_store.get(data.dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    # Get steps
    from app.models.pipeline import PipelineStep
    steps = db.query(PipelineStep).filter(PipelineStep.pipeline_id == data.pipeline_id).order_by(PipelineStep.order).all()
    import json
    steps_list = [
        {
            "order": s.order,
            "transformation": s.transformation,
            "params": json.loads(s.params) if s.params else {}
        }
        for s in steps
    ]
    
    # Run preview
    preview_res = preview_pipeline_execution(df, steps_list)
    return preview_res

@router.post("/run")
def run_endpoint(data: PipelineRun, db: Session = Depends(get_db)):
    try:
        run_res = pipeline_orchestrator.run_pipeline(
            db=db,
            pipeline_id=data.pipeline_id,
            dataset_id=data.dataset_id
        )
        if run_res is None:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        return run_res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error running pipeline: {str(e)}")

@router.get("/history", response_model=List[Dict[str, Any]])
def history_endpoint(
    pipeline_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return pipeline_history.list_runs(db, pipeline_id, dataset_id)

@router.post("/template/apply")
def apply_template_endpoint(data: ApplyTemplate, db: Session = Depends(get_db)):
    # Validate template name
    templates = get_available_templates()
    if data.template_name not in templates:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid template name. Must be one of: {', '.join(templates)}"
        )
        
    success = pipeline_orchestrator.apply_template(
        db=db,
        pipeline_id=data.pipeline_id,
        template_name=data.template_name,
        dataset_id=data.dataset_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Pipeline not found")
        
    return {"message": f"Predefined template '{data.template_name}' applied successfully"}

@router.post("/export")
def export_endpoint(data: PipelineExport, db: Session = Depends(get_db)):
    # Validate format
    fmt = data.format.lower()
    valid_formats = ["json", "yaml", "template", "execution_report", "audit_report"]
    if fmt not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid export format. Must be one of: {', '.join(valid_formats)}"
        )
        
    if fmt in ["json", "yaml", "template"]:
        if not data.pipeline_id:
            raise HTTPException(status_code=400, detail="pipeline_id is required for json, yaml, and template formats")
            
        pipeline = pipeline_orchestrator.get_pipeline(db, data.pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
            
        from app.models.pipeline import PipelineStep
        steps = db.query(PipelineStep).filter(PipelineStep.pipeline_id == data.pipeline_id).order_by(PipelineStep.order).all()
        
        if fmt == "json":
            return pipeline_exporter.export_pipeline_as_json(pipeline, steps)
        elif fmt == "yaml":
            yaml_str = pipeline_exporter.export_pipeline_as_yaml(pipeline, steps)
            return {"format": "yaml", "content": yaml_str}
        else:
            return pipeline_exporter.export_pipeline_as_template(pipeline, steps)
            
    else: # report formats
        if not data.run_id:
            raise HTTPException(status_code=400, detail="run_id is required for report formats")
            
        run_details = pipeline_history.get_run(db, data.run_id)
        if not run_details:
            raise HTTPException(status_code=404, detail="Pipeline run execution not found")
            
        if fmt == "execution_report":
            report_str = pipeline_exporter.generate_execution_report(run_details)
            return {"format": "execution_report", "content": report_str}
        else:
            audit_str = pipeline_exporter.generate_audit_report(run_details)
            return {"format": "audit_report", "content": audit_str}
