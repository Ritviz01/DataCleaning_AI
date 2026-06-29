import polars as pl
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.dataset_store import dataset_store
from app.services.copilot.intent_parser import parse_intent
from app.services.copilot.dataset_context import build_dataset_context
from app.services.copilot.prompt_builder import build_copilot_prompt
from app.services.copilot.pipeline_generator import generate_pipeline
from app.services.copilot.pipeline_validator import validate_copilot_pipeline
from app.services.copilot.conversation_memory import copilot_memory
from app.services.pipeline_engine.preview_engine import preview_pipeline_execution
from app.services.pipeline_engine import pipeline_orchestrator

def generate_intelligent_pipeline(
    dataset_id: str,
    prompt: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Orchestrates the AI Copilot workflow:
    1. Parse intent
    2. Extract context
    3. Retrieve session memory
    4. Construct prompt and generate pipeline via LLM
    5. Validate pipeline against dataset
    6. Generate dry-run preview
    7. Save turn to memory
    """
    df = dataset_store.get(dataset_id)
    if df is None:
        raise ValueError(f"Dataset '{dataset_id}' not found.")
        
    # 1. Parse intent
    intent = parse_intent(prompt)
    
    # 2. Extract compact schema context
    context = build_dataset_context(df)
    
    # 3. Retrieve conversation history
    history = []
    if session_id:
        history = copilot_memory.get_history(session_id)
        
    # 4. Construct prompt and generate
    llm_prompt = build_copilot_prompt(prompt, context, history)
    pipeline_data = generate_pipeline(llm_prompt)
    
    # 5. Validate the generated pipeline
    validation = validate_copilot_pipeline(df, pipeline_data)
    
    # 6. Generate dry-run preview
    preview = {}
    if validation.get("valid"):
        try:
            preview = preview_pipeline_execution(df, pipeline_data.get("steps", []))
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append({
                "step_index": 0,
                "field": "preview",
                "message": f"Preview execution failed: {str(e)}"
            })
            
    # 7. Save to conversation memory
    if session_id:
        copilot_memory.add_turn(
            session_id=session_id,
            question=prompt,
            answer=pipeline_data.get("description", ""),
            generated_pipeline=pipeline_data
        )
        
    return {
        "pipeline": pipeline_data,
        "validation": validation,
        "preview": preview
    }

def run_intelligent_pipeline(
    db: Session,
    pipeline_data: Dict[str, Any],
    dataset_id: str
) -> Dict[str, Any]:
    """
    Saves and executes the copilot-generated pipeline using the existing pipeline engine.
    Ensures 100% reuse of orchestrator, templates, database runs, and audit logs.
    """
    description_text = pipeline_data.get("description", "AI Generated Pipeline")
    if "AI Generated" not in description_text:
        description_text = f"[AI Generated] {description_text}"
        
    pipeline = pipeline_orchestrator.create_pipeline(
        db=db,
        name=pipeline_data.get("pipeline_name", "AI Copilot Pipeline"),
        description=description_text
    )
    
    # 2. Persist pipeline steps
    steps = pipeline_data.get("steps") or []
    for step in steps:
        pipeline_orchestrator.add_step(
            db=db,
            pipeline_id=pipeline.id,
            transformation=step["transformation"],
            params=step["params"],
            order=step.get("order")
        )
        
    # 3. Execute using the orchestrator
    run_result = pipeline_orchestrator.run_pipeline(
        db=db,
        pipeline_id=pipeline.id,
        dataset_id=dataset_id
    )
    
    return run_result
