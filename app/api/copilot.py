from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.services.copilot import copilot_service
from app.services.copilot.conversation_memory import copilot_memory
from app.services.dataset_store import dataset_store
from app.services.pipeline_engine.preview_engine import preview_pipeline_execution
from app.models.pipeline import Pipeline

router = APIRouter(prefix="/copilot", tags=["copilot"])

# ==========================================
# Pydantic Request/Response Schemas
# ==========================================

class CopilotGenerateRequest(BaseModel):
    dataset_id: str
    prompt: str = Field(..., min_length=1)
    session_id: Optional[str] = None

class CopilotPreviewRequest(BaseModel):
    dataset_id: str
    pipeline_data: Dict[str, Any]

class CopilotRunRequest(BaseModel):
    dataset_id: str
    pipeline_data: Dict[str, Any]

# ==========================================
# Route Handlers
# ==========================================

@router.post("/generate")
def generate_pipeline_endpoint(req: CopilotGenerateRequest):
    try:
        res = copilot_service.generate_intelligent_pipeline(
            dataset_id=req.dataset_id,
            prompt=req.prompt,
            session_id=req.session_id
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate pipeline: {str(e)}")

@router.post("/preview")
def preview_pipeline_endpoint(req: CopilotPreviewRequest):
    df = dataset_store.get(req.dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    steps = req.pipeline_data.get("steps") or []
    try:
        preview_res = preview_pipeline_execution(df, steps)
        return preview_res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Preview execution failed: {str(e)}")

@router.post("/run")
def run_pipeline_endpoint(req: CopilotRunRequest, db: Session = Depends(get_db)):
    try:
        run_res = copilot_service.run_intelligent_pipeline(
            db=db,
            pipeline_data=req.pipeline_data,
            dataset_id=req.dataset_id
        )
        return run_res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@router.get("/history")
def get_history_endpoint(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    # 1. If session_id is provided, check session conversation memory
    session_history = []
    if session_id:
        session_history = copilot_memory.get_history(session_id)
        
    # 2. Query persistent database for AI-generated pipelines
    db_pipelines = db.query(Pipeline).filter(
        (Pipeline.description.like("%AI Generated%")) | 
        (Pipeline.name.like("%AI Copilot%"))
    ).order_by(Pipeline.created_at.desc()).all()
    
    formatted_db_history = [
        {
            "pipeline_id": p.id,
            "name": p.name,
            "description": p.description,
            "dataset_id": p.dataset_id,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in db_pipelines
    ]
    
    return {
        "session_history": session_history,
        "saved_pipelines": formatted_db_history
    }
