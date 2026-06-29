import re
from typing import Dict, Any, List

def parse_intent(prompt: str) -> Dict[str, Any]:
    """
    Parses natural language user instructions into structured goals and candidate actions.
    Recognizes key synonyms like: clean, fix, repair, standardize, normalize, prepare, optimize, analyze, transform.
    """
    prompt_lower = prompt.lower().strip()
    
    # 1. Determine Goal
    goal = "cleaning" # default goal
    
    ml_keywords = ["machine learning", "ml", "train", "predict", "model", "preprocessing"]
    bi_keywords = ["power bi", "powerbi", "bi", "tableau", "dashboard", "power_bi", "report"]
    analytics_keywords = ["analytics", "prep", "prepare", "optimize", "ready", "analysis", "transform"]
    
    if any(kw in prompt_lower for kw in ml_keywords):
        goal = "machine_learning"
    elif any(kw in prompt_lower for kw in bi_keywords):
        goal = "power_bi"
    elif any(kw in prompt_lower for kw in analytics_keywords):
        goal = "analytics_preparation"
        
    # 2. Extract Candidate Actions based on keywords/synonyms
    actions = []
    
    # Check for duplicates keyword
    if any(kw in prompt_lower for kw in ["duplicate", "duplicates", "dedup", "double"]):
        actions.append("remove_duplicates")
        
    # Check for missing values keyword
    if any(kw in prompt_lower for kw in ["missing", "null", "nan", "fill", "impute", "empty"]):
        actions.append("fill_missing")
        
    # Check for outliers
    if any(kw in prompt_lower for kw in ["outlier", "outliers", "anomaly", "anomalies", "cap"]):
        actions.append("remove_outliers")
        
    # Check for normalize
    if any(kw in prompt_lower for kw in ["normalize", "normalize", "scale", "standardize"]):
        actions.append("normalize")
        
    # Check for dates
    if any(kw in prompt_lower for kw in ["date", "dates", "time"]):
        actions.append("standardize_dates")
        
    # Check for categoricals / encoding
    if any(kw in prompt_lower for kw in ["category", "categories", "categorical", "encode", "one-hot", "onehot"]):
        actions.append("encode_categories")
        
    # Check for currency or numeric conversion
    if any(kw in prompt_lower for kw in ["currency", "currencies", "money", "numeric", "number", "numbers"]):
        actions.append("convert_numeric")

    # Check for text clean / trim
    if any(kw in prompt_lower for kw in ["trim", "whitespace", "space", "spaces", "strip"]):
        actions.append("trim_whitespace")

    # If ML goal is set and actions is empty, populate with default ML pipeline actions
    if goal == "machine_learning" and not actions:
        actions = ["clean", "convert_types", "encode_categories", "normalize"]
    # If Power BI goal is set and actions is empty, populate with default Power BI actions
    elif goal == "power_bi" and not actions:
        actions = ["clean", "convert_types", "standardize_text"]
    # If general cleaning is requested and no specific actions are mentioned
    elif not actions:
        actions = ["clean"]
        
    return {
        "goal": goal,
        "actions": actions
    }
