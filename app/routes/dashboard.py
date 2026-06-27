from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from app.services.dashboard_service import create_dashboard

router = APIRouter(prefix="/datasets", tags=["dashboard"])

class DashboardRequest(BaseModel):
    dataset_id: str

class DashboardResponse(BaseModel):
    dataset_id: str
    domain: str
    title: str
    specification: Dict[str, Any]
    explanation: Dict[str, Any]

@router.post("/dashboard", response_model=DashboardResponse)
async def generate_dashboard(request: DashboardRequest):
    """
    Generate an AI dashboard specification, calculate KPIs via Polars,
    and generate expected business insights and descriptions.
    """
    try:
        res = create_dashboard(request.dataset_id)
        return DashboardResponse(
            dataset_id=res["dataset_id"],
            domain=res["domain"],
            title=res["title"],
            specification=res["specification"],
            explanation=res["explanation"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate dashboard: {str(e)}")


@router.get("/dashboard/{dataset_id}")
async def get_dashboard(dataset_id: str):
    """
    Retrieve stored dashboard JSON.
    """
    from app.services.dashboard_service import get_dashboard_from_db
    try:
        dash = get_dashboard_from_db(dataset_id)
        if not dash:
            # Try to generate on the fly if the dataset exists
            res = create_dashboard(dataset_id)
            dash = res["specification"]
        return dash
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve dashboard: {str(e)}")


@router.post("/dashboard/{dataset_id}/generate")
async def regenerate_dashboard(dataset_id: str):
    """
    Force regeneration of the dashboard.
    """
    from app.services.dataset_store import get_dataset
    from app.services.pipeline import analyse_dataset
    from app.services.dashboard_service import generate_dashboard, save_dashboard_to_db
    
    df = get_dataset(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail=f"Dataset with ID '{dataset_id}' not found.")
        
    try:
        analysis = analyse_dataset(df)
        spec = generate_dashboard(df, analysis["schema"], analysis["profile"], analysis["insights"])
        save_dashboard_to_db(dataset_id, spec)
        return spec
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to regenerate dashboard: {str(e)}")
