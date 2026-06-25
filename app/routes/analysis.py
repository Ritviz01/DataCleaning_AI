from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

from app.services.query_engine import run_analysis

router = APIRouter(tags=["analysis"])

class AskRequest(BaseModel):
    dataset_id: str
    question: str

class AskResponse(BaseModel):
    question: str
    answer: str
    query_plan: Dict[str, Any]
    table: List[Dict[str, Any]]
    insight: str

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Ask a natural language question about an uploaded dataset.
    Generates a structured JSON query plan, validates it, executes it safely, and returns insights.
    """
    try:
        res = run_analysis(request.dataset_id, request.question)
        return AskResponse(
            question=res["question"],
            answer=res["answer"],
            query_plan=res["query_plan"],
            table=res["table"],
            insight=res["insight"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing question: {str(e)}")
