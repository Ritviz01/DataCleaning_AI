from typing import Any, Dict
import polars as pl
from app.services.dataset_store import get_dataset
from app.services.conversation_memory import conversation_memory
from app.services.pipeline import analyse_dataset
from app.services.dataset_classifier import classify_dataset
from app.services.dataframe_agent import generate_operations
from app.services.query_validator import validate_plan
from app.services.query_executor import execute_plan
from app.services.query_insight_generator import generate_query_insights

def run_analysis(dataset_id: str, question: str) -> dict:
    """Orchestrates the conversational data analyst query lifecycle:
    
    1. Loads dataset and history.
    2. Runs analysis & classification.
    3. Prompts LLM for a structured JSON query plan.
    4. Validates and executes query plan using Polars.
    5. Generates business insights and natural language answer.
    6. Saves turn to conversation memory.
    """
    df = get_dataset(dataset_id)
    if df is None:
        raise ValueError(f"Dataset with ID '{dataset_id}' not found.")

    # 1. Retrieve schema and metadata
    analysis = analyse_dataset(df)
    metadata = analysis["metadata"]
    schema = analysis["schema"]
    
    # Classify dataset type
    class_res = classify_dataset(metadata, metadata.get("column_names", []), schema)
    dataset_type = class_res.get("dataset_type", "General")

    # 2. Get history
    history = conversation_memory.get_history(dataset_id)

    # 3. Call dataframe agent to get plan and description
    plan = generate_operations(question, metadata, schema, dataset_type, history)

    # 4. Validate the plan
    validate_plan(plan, df)

    # 5. Execute the plan
    res_df = execute_plan(plan, df)
    table = res_df.to_dicts()

    # 6. Generate insights
    insight = generate_query_insights(question, table, metadata, schema)

    # Extract answer/explanation from LLM plan, fallback to a default
    answer = plan.get("answer") or plan.get("explanation") or f"Query executed successfully using {len(plan.get('steps', []))} steps."

    # 7. Save turn in memory
    conversation_memory.add_turn(
        dataset_id=dataset_id,
        question=question,
        answer=answer,
        query_plan=plan,
        insight=insight
    )

    return {
        "question": question,
        "answer": answer,
        "query_plan": plan,
        "table": table,
        "insight": insight
    }

# Retain generate_query_plan for backwards compatibility
def generate_query_plan(question: str, dataset_metadata: dict, schema: list[dict]) -> dict:
    """Backwards compatible query plan generation."""
    from app.services.dataframe_agent import generate_operations as legacy_gen
    # We pass empty history and General dataset type
    return legacy_gen(question, dataset_metadata, schema, "General", [])
