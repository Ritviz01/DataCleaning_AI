import os
from openai import OpenAI
from app.services.prompt_builder import build_dataset_prompt

def validate_and_sanitize_response(text: str, schema: list, metadata: dict) -> str:
    # Extract lowercased column names
    column_names = metadata.get("column_names", []) if metadata else []
    if not column_names and schema:
        column_names = [col.get("column_name") for col in schema]
    col_lowered = [c.lower().strip() for c in column_names if c]
    
    # Mapping of target forbidden keywords to their required column name indicators
    checks = {
        "revenue": ["revenue", "income"],
        "profit": ["profit", "earnings"],
        "sales": ["sales", "transaction", "order", "sold", "sale"],
        "market share": ["market share"],
        "growth rate": ["growth rate", "growth", "trend"],
        "employees": ["employee", "staff", "workforce", "employees"]
    }
    
    lines = text.split("\n")
    cleaned_lines = []
    
    for line in lines:
        line_lower = line.lower()
        keep = True
        for term, columns in checks.items():
            if term in line_lower:
                # If no matching columns are in the dataset, filter out this line
                if not any(col in col_lowered for col in columns):
                    keep = False
                    break
        if keep:
            cleaned_lines.append(line)
            
    return "\n".join(cleaned_lines)

def get_llm_analysis(
    metadata,
    schema,
    quality,
    issues,
    profile=None,
    recommendations=None,
    type_suggestions=None,
    sample_rows=None,
    business_context=None
):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)

    prompt = build_dataset_prompt(
        metadata=metadata,
        schema=schema,
        quality=quality,
        issues=issues,
        profile=profile,
        recommendations=recommendations,
        type_suggestions=type_suggestions,
        sample_rows=sample_rows,
        business_context=business_context
    )

    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        messages=[
            {
                "role": "system",
                "content": "You are a Senior Data Analyst and Data Quality Consultant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content
    
    # Apply post-processing validation layer
    return validate_and_sanitize_response(content, schema, metadata)

def generate_ai_insights(analysis: dict, business_context: dict) -> str:
    sample_rows = business_context.get("sample_rows", [])
    return get_llm_analysis(
        metadata=analysis.get("metadata"),
        schema=analysis.get("schema"),
        quality=analysis.get("quality"),
        issues=analysis.get("issues"),
        profile=analysis.get("profile"),
        recommendations=analysis.get("recommendations"),
        type_suggestions=analysis.get("type_suggestions"),
        sample_rows=sample_rows,
        business_context=business_context
    )