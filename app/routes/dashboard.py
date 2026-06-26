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
