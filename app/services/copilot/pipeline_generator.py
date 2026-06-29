import os
import json
from openai import OpenAI
from typing import Dict, Any, List, Optional

def generate_pipeline(prompt: str, retries: int = 3) -> Dict[str, Any]:
    """
    Calls the configured OpenAI LLM, validates JSON syntax, handles naming variations,
    and returns a structured pipeline dictionary.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    
    current_prompt = prompt
    last_error = None
    
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional Python data analyst. You always return responses in JSON format."
                    },
                    {
                        "role": "user",
                        "content": current_prompt
                    }
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            
            # Strip markdown blocks if returned
            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
                
            if not content:
                raise ValueError("LLM returned an empty response")
                
            pipeline_data = json.loads(content)
            
            # Normalize step names: support both 'operation'/'parameters' and 'transformation'/'params'
            normalized_pipeline = normalize_pipeline_keys(pipeline_data)
            return normalized_pipeline
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            last_error = e
            # Try to refine the prompt for retry
            current_prompt = prompt + f"\n\n[Warning: Your previous attempt failed with error: {str(e)}. Please correct your JSON structure and output ONLY the valid JSON format specified.]"
            
    raise RuntimeError(f"Failed to generate valid pipeline JSON after {retries} attempts. Last error: {last_error}")

def normalize_pipeline_keys(pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardizes output format, mapping 'operation' -> 'transformation' and 'parameters' -> 'params'
    if the LLM returns the alternate names.
    """
    name = pipeline_data.get("pipeline_name") or pipeline_data.get("name") or "AI Cleaning Pipeline"
    desc = pipeline_data.get("description") or "AI Generated Pipeline"
    steps = pipeline_data.get("steps") or []
    
    normalized_steps = []
    for idx, step in enumerate(steps):
        # Map operation -> transformation
        transformation = step.get("transformation") or step.get("operation")
        if not transformation:
            # Skip invalid step or try to fallback
            continue
            
        # Map parameters -> params
        params = step.get("params") or step.get("parameters") or {}
        if not isinstance(params, dict):
            params = {}
            
        normalized_steps.append({
            "order": idx + 1,
            "transformation": transformation,
            "params": params
        })
        
    return {
        "pipeline_name": name,
        "description": desc,
        "steps": normalized_steps
    }
