import json
import os
from openai import OpenAI
from app.services.prompt_builder import build_analyst_prompt

def generate_operations(
    question: str, 
    dataset_metadata: dict, 
    schema: list[dict], 
    dataset_type: str, 
    history: list[dict]
) -> dict:
    """Uses LLM to convert a user question and history into a structured JSON query plan."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    
    prompt = build_analyst_prompt(question, dataset_metadata, schema, dataset_type, history)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a professional Python data analyst specializing in Polars. You always return responses in JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content.strip()
    
    # Strip markdown block formatting if present
    if content.startswith("```"):
        lines = content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()
        
    try:
        data = json.loads(content)
        return data
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse LLM JSON response: {e}. Raw content: {content}")
