import json
import os
from openai import OpenAI

def classify_dataset_locally(column_names: list[str]) -> dict:
    cols = [c.lower().strip() for c in column_names]
    # Simple heuristics mapping
    if any(k in cols for k in ["student", "enrollment", "course", "grade", "gpa"]):
        return {"dataset_type": "Education", "confidence": 0.90}
    if any(k in cols for k in ["employee", "attrition", "salary", "hr", "hire"]):
        return {"dataset_type": "HR", "confidence": 0.90}
    if any(k in cols for k in ["revenue", "profit", "budget", "finance", "expense"]):
        return {"dataset_type": "Finance", "confidence": 0.90}
    if any(k in cols for k in ["patient", "doctor", "health", "hospital", "diagnosis"]):
        return {"dataset_type": "Healthcare", "confidence": 0.90}
    if any(k in cols for k in ["product", "order", "price", "cart", "customer"]):
        return {"dataset_type": "Ecommerce", "confidence": 0.90}
    if any(k in cols for k in ["sale", "sold", "deals", "revenue", "opportunity"]):
        return {"dataset_type": "Sales", "confidence": 0.90}
    return {"dataset_type": "CRM", "confidence": 0.70}

def classify_dataset(metadata: dict, column_names: list[str], schema: list[dict]) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return classify_dataset_locally(column_names)
        
    client = OpenAI(api_key=api_key)
    
    prompt = f"""You are a database classification service.
Given the following dataset metadata and column descriptions, classify the dataset into exactly one of these domains:
HR, Finance, Healthcare, Education, Ecommerce, Marketing, Sales, Manufacturing, CRM, Logistics, Real Estate.

Dataset Details:
- Metadata: {metadata}
- Columns: {column_names}
- Schema details: {schema}

Return your response in raw JSON format (no markdown blocks, just raw JSON) containing exactly two keys:
1. "dataset_type": (one of the domains listed above)
2. "confidence": (a float between 0.0 and 1.0 representing classification confidence)

Example:
{{
  "dataset_type": "Education",
  "confidence": 0.96
}}
"""
    try:
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[
                {"role": "system", "content": "You are a database domain classification service. Output raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception:
        return classify_dataset_locally(column_names)
