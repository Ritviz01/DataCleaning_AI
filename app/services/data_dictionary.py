import os
import json
from openai import OpenAI

def generate_dictionary_locally(schema: list[dict]) -> dict:
    dictionary = {}
    for col in schema:
        name = col.get("column_name", "")
        semantic = col.get("semantic_type", "UNKNOWN")
        dtype = col.get("data_type", "String")
        
        desc = f"Column containing {semantic.lower()} values of data type {dtype}."
        if name.lower() in ["price", "cost", "amount", "fee"]:
            desc = "Product selling price or monetary transaction amount."
        elif name.lower() in ["id", "customer_id", "student_id", "course_id", "user_id"]:
            desc = "Unique database identifier key."
        elif name.lower() in ["name", "student_name", "user_name"]:
            desc = "Full name of the record entity."
        elif name.lower() in ["age"]:
            desc = "Age demographics."
        elif name.lower() in ["ram", "cpu", "gpu", "memory"]:
            desc = "Technical hardware system component specifications."
            
        dictionary[name] = {"description": desc}
    return dictionary

def generate_dictionary(schema: list[dict], metadata: dict) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return generate_dictionary_locally(schema)
        
    client = OpenAI(api_key=api_key)
    
    prompt = f"""You are a database documentation agent.
Given the following schema definitions, generate a business-friendly description for every single column name.

Columns:
{[col.get("column_name") for col in schema]}

Schema details:
{schema}

Return your response in raw JSON format (no markdown blocks, just raw JSON) where the keys are the column names, and the values are objects containing a "description" string.

Example:
{{
  "Price": {{
    "description": "Product selling price"
  }},
  "Customer_ID": {{
    "description": "Unique identifier for each customer"
  }}
}}
"""
    try:
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[
                {"role": "system", "content": "You are a metadata documentation service. Output raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception:
        return generate_dictionary_locally(schema)
