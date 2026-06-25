from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, List, Dict

from app.services.dataset_store import dataset_store
from app.services.pipeline import analyse_dataset
from app.services.query_engine import generate_query_plan
from app.services.query_executor import execute_query
from app.services.query_insight_generator import generate_query_insights

router = APIRouter(tags=["analysis"])

class AskRequest(BaseModel):
    dataset_id: str
    question: str

class AskResponse(BaseModel):
    question: str
    answer: str
    data: List[Dict[str, Any]]

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Ask a natural language question about an uploaded dataset.
    Generates a Polars query plan, executes it safely, and returns insights and result table.
    """
    df = dataset_store.get(request.dataset_id)
    if df is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Dataset with ID '{request.dataset_id}' not found or could not be loaded."
        )

    # 1. Retrieve schema and metadata of the dataset
    try:
        analysis = analyse_dataset(df)
        metadata = analysis["metadata"]
        schema = analysis["schema"]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze dataset schema and metadata: {str(e)}"
        )

    # 2. Generate the query plan via query engine / dataframe agent
    try:
        plan = generate_query_plan(request.question, metadata, schema)
        polars_code = plan.get("polars_code")
        explanation = plan.get("explanation", "Executed query on dataset.")
        required_columns = plan.get("required_columns", [])
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to generate query plan from the question: {str(e)}"
        )

    if not polars_code:
        raise HTTPException(
            status_code=500,
            detail="The dataframe agent returned an empty query plan."
        )

    # 3. Safely execute the query
    exec_res = execute_query(polars_code, df, required_columns)
    if not exec_res["success"]:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to safely execute generated query: {exec_res.get('error')}. Generated code: {polars_code}"
        )

    result_data = exec_res["result"]
    
    # Standardize result data to a list of dicts (result table)
    # If the result is a single value, wrap it inside a dictionary/list format
    if not isinstance(result_data, list):
        result_table = [{"result": result_data}]
    else:
        # If it is a list of scalars (e.g. from series), format it as dicts
        if result_data and not isinstance(result_data[0], dict):
            result_table = [{"value": val} for val in result_data]
        else:
            result_table = result_data

    # 4. Generate AI insights from query results
    try:
        insights = generate_query_insights(request.question, result_table, metadata, schema)
    except Exception as e:
        # Fall back to a default insight message if LLM fails
        insights = f"Could not generate insights: {str(e)}"

    # 5. Format answer combining explanation and insights
    formatted_answer = f"{explanation}\n\nInsights:\n{insights}"

    return AskResponse(
        question=request.question,
        answer=formatted_answer,
        data=result_table
    )
