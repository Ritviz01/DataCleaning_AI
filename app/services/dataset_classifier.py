import json
import os
from openai import OpenAI

DOMAINS = {
    "Education": ["student", "enrollment", "course", "grade", "gpa", "school", "teacher", "tuition", "class", "academic"],
    "HR": ["employee", "attrition", "salary", "hr", "hire", "department", "job_title", "tenure", "termination", "work_years"],
    "Finance": ["revenue", "profit", "budget", "finance", "expense", "cost", "tax", "margin", "income", "balance", "debt"],
    "Healthcare": ["patient", "doctor", "health", "hospital", "diagnosis", "clinic", "treatment", "medical", "disease", "symptom"],
    "Ecommerce": ["product", "order", "price", "cart", "customer", "checkout", "sku", "shipping", "transaction", "purchase"],
    "Sales": ["sale", "sold", "deals", "revenue", "opportunity", "pipeline", "quota", "seller", "deal_size", "win_rate"],
    "CRM": ["contact", "lead", "opportunity", "account", "interaction", "feedback", "support", "ticket", "customer_id", "service_request"],
    "Marketing": ["campaign", "clicks", "impressions", "conversion", "leads", "spend", "ad_id", "ctr", "marketing"],
    "Logistics": ["shipment", "delivery", "tracking", "warehouse", "carrier", "route", "inventory", "fleet", "destination", "origin"],
    "Real Estate": ["property", "listing", "house", "rent", "lease", "agent", "sqft", "price_sqft", "address", "bedroom", "bathroom"],
    "Manufacturing": ["equipment", "production", "batch", "quality", "machine", "maintenance", "downtime", "factory", "sensor", "defect"],
    "Electronics": ["cpu", "gpu", "ram", "memory", "storage", "screen", "processor", "brand", "laptop", "battery", "opsys", "typename", "weight_kg"],
    "Retail": ["store", "inventory", "stock", "cashier", "transaction", "sku", "barcode", "aisle", "pos", "retail"],
    "Energy": ["power", "electricity", "grid", "fuel", "solar", "wind", "consumption", "kilowatt", "generator", "utility"],
    "Transportation": ["passenger", "ticket", "flight", "train", "bus", "route", "station", "booking", "trip", "fare"],
    "Hospitality": ["hotel", "room", "booking", "guest", "reservation", "stay", "checkin", "checkout", "lodging", "amenities"],
    "Social Media": ["post", "like", "share", "comment", "follower", "tweet", "hashtag", "engagement", "views", "username"],
    "Entertainment": ["movie", "music", "game", "rating", "genre", "duration", "stream", "artist", "album", "release_year"],
    "Automotive": ["car", "vehicle", "engine", "mileage", "make", "model", "transmission", "fuel_type", "odometer", "vin"],
    "Telecom": ["phone", "plan", "subscriber", "usage", "data_gb", "call_duration", "carrier", "roaming", "churn", "billing"]
}

def classify_dataset_locally(column_names: list[str]) -> dict:
    cols = [c.lower().strip() for c in column_names]
    best_domain = "CRM"
    best_matches = 0
    
    for domain, keywords in DOMAINS.items():
        matches = sum(1 for col in cols if any(kw in col for kw in keywords))
        if matches > best_matches:
            best_matches = matches
            best_domain = domain
            
    if best_matches > 0:
        confidence = 0.90 if best_matches >= 2 else 0.80
        return {"dataset_type": best_domain, "confidence": confidence}
    
    return {"dataset_type": "CRM", "confidence": 0.70}

def classify_dataset(metadata: dict, column_names: list[str], schema: list[dict]) -> dict:
    local_res = classify_dataset_locally(column_names)
    if local_res["confidence"] >= 0.75:
        return local_res
        
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return local_res
        
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
        return local_res

