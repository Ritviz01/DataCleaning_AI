import os
import re
from openai import OpenAI
from app.services.prompt_builder import build_dataset_prompt

def sanitize_text(data: any, schema: list = None, metadata: dict = None) -> any:
    """Recursively traverses a JSON-like object (dict, list, str) and sanitizes string values
    at the sentence level. Removes sentences containing business terms if the corresponding
    columns/semantic types are not present in the dataset.
    """
    if isinstance(data, dict):
        return {k: sanitize_text(v, schema, metadata) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_text(item, schema, metadata) for item in data]
    elif isinstance(data, str):
        # Extract lowercased column names
        column_names = []
        if metadata:
            cols_val = metadata.get("column_names") or metadata.get("columns")
            if isinstance(cols_val, list):
                column_names = cols_val
            elif isinstance(metadata.get("column_names"), list):
                column_names = metadata.get("column_names")
                
        if not column_names and schema:
            column_names = [col.get("column_name") for col in schema if isinstance(col, dict)]
            
        if not isinstance(column_names, list):
            column_names = []
            
        col_lowered = [str(c).lower().strip() for c in column_names if c]
        
        # If no schema and no metadata/columns are provided, do not filter anything
        if not col_lowered:
            return data
        
        # Define checked terms and their corresponding column name keywords/indicators
        checks = {
            "revenue": ["revenue", "rev", "income", "turnover", "price", "cost", "msrp", "amount"],
            "profit": ["profit", "margin", "earnings", "income", "revenue"],
            "sales": ["sales", "sale", "sold", "transaction", "order", "price", "amount"],
            "orders": ["order", "purchase", "transaction", "sales", "sold"],
            "customer retention": ["customer", "retention", "loyalty", "cohort", "churn"],
            "retention": ["customer", "retention", "loyalty", "cohort", "churn"],
            "employees": ["employee", "staff", "workforce", "hire", "attrition"]
        }
        
        # Split text into sentences using simple regex looking for sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', data)
        cleaned_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            keep = True
            for term, required_keywords in checks.items():
                if term in sentence_lower:
                    if not any(k in col_lowered for k in required_keywords):
                        keep = False
                        break
            if keep:
                cleaned_sentences.append(sentence)
                
        return " ".join(cleaned_sentences)
    else:
        return data

def validate_and_sanitize_response(text: str, schema: list, metadata: dict) -> str:
    return sanitize_text(text, schema, metadata)

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