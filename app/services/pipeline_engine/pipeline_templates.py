from typing import List, Dict, Any

TEMPLATES = {
    "Basic Cleaning": [
        {"transformation": "remove_duplicates", "params": {}},
        {"transformation": "trim_whitespace", "params": {}}
    ],
    "Advanced Cleaning": [
        {"transformation": "remove_duplicates", "params": {}},
        {"transformation": "trim_whitespace", "params": {}},
        {"transformation": "standardize_text", "params": {}}
    ],
    "Financial Dataset Cleaning": [
        {"transformation": "remove_duplicates", "params": {}},
        {"transformation": "trim_whitespace", "params": {}}
    ],
    "Healthcare Dataset Cleaning": [
        {"transformation": "remove_duplicates", "params": {}},
        {"transformation": "trim_whitespace", "params": {}}
    ],
    "Retail Dataset Cleaning": [
        {"transformation": "remove_duplicates", "params": {}},
        {"transformation": "trim_whitespace", "params": {}}
    ],
    "HR Dataset Cleaning": [
        {"transformation": "remove_duplicates", "params": {}},
        {"transformation": "trim_whitespace", "params": {}}
    ],
    "ML Preprocessing": [
        {"transformation": "remove_duplicates", "params": {}},
        {"transformation": "trim_whitespace", "params": {}}
    ],
    "Analytics Preparation": [
        {"transformation": "remove_duplicates", "params": {}},
        {"transformation": "trim_whitespace", "params": {}}
    ]
}

def get_available_templates() -> List[str]:
    return list(TEMPLATES.keys())

def get_template_steps(template_name: str, schema: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Returns steps for a predefined template. If schema is provided, 
    dynamically adds column-specific steps tailored to column types and semantics.
    """
    if template_name not in TEMPLATES:
        raise ValueError(f"Unknown template: '{template_name}'")
    
    # Base steps
    steps = [
        {"transformation": "remove_duplicates", "params": {}},
        {"transformation": "trim_whitespace", "params": {}}
    ]
    
    if not schema:
        # Return generic steps for the template type if no schema
        if template_name == "Advanced Cleaning":
            steps.append({"transformation": "standardize_text", "params": {}})
        return steps
    
    # Find key column types
    numeric_cols = []
    categorical_cols = []
    text_cols = []
    date_cols = []
    
    for col in schema:
        col_name = col.get("column_name")
        dtype = col.get("type", "String").lower()
        semantic = col.get("semantic_type", "UNKNOWN")
        
        if "int" in dtype or "float" in dtype or "double" in dtype or semantic in ["AGE", "PRICE", "MEASUREMENT", "COUNT"]:
            numeric_cols.append(col_name)
        elif semantic == "DATE":
            date_cols.append(col_name)
        elif semantic in ["TEXT", "DESCRIPTION"]:
            text_cols.append(col_name)
        else:
            categorical_cols.append(col_name)
            
    # Tailor based on template
    if template_name == "Basic Cleaning":
        # Add fill missing median for numeric columns
        for col in numeric_cols[:3]: # Limit to first 3 columns to keep it clean
            steps.append({"transformation": "fill_missing", "params": {"column": col, "method": "median"}})
            
    elif template_name == "Advanced Cleaning":
        for col in numeric_cols[:2]:
            steps.append({"transformation": "fill_missing", "params": {"column": col, "method": "median"}})
        for col in date_cols:
            steps.append({"transformation": "fill_missing", "params": {"column": col, "method": "forward_fill"}})
        steps.append({"transformation": "standardize_text", "params": {}})
        
    elif template_name in ["Financial Dataset Cleaning", "Financial Dataset"]:
        # Add float conversions and outlier capping
        for col in numeric_cols[:3]:
            steps.append({"transformation": "convert_type", "params": {"column": col, "target_type": "Float"}})
            steps.append({"transformation": "remove_outliers", "params": {"column": col, "method": "cap"}})
            
    elif template_name in ["Healthcare Dataset Cleaning", "Healthcare Dataset"]:
        for col in date_cols:
            steps.append({"transformation": "fill_missing", "params": {"column": col, "method": "forward_fill"}})
        for col in numeric_cols[:2]:
            steps.append({"transformation": "remove_outliers", "params": {"column": col, "method": "cap"}})
            
    elif template_name in ["Retail Dataset Cleaning", "Retail Dataset"]:
        for col in categorical_cols[:2]:
            steps.append({"transformation": "fill_missing", "params": {"column": col, "method": "mode"}})
        for col in numeric_cols[:2]:
            steps.append({"transformation": "normalize", "params": {"column": col, "method": "min_max"}})
            
    elif template_name in ["HR Dataset Cleaning", "HR Dataset"]:
        for col in categorical_cols[:2]:
            steps.append({"transformation": "fill_missing", "params": {"column": col, "method": "mode"}})
            steps.append({"transformation": "encode_categories", "params": {"column": col, "method": "label"}})
            
    elif template_name == "ML Preprocessing":
        # Convert types, handle missing, normalize and encode
        for col in numeric_cols[:2]:
            steps.append({"transformation": "fill_missing", "params": {"column": col, "method": "median"}})
            steps.append({"transformation": "normalize", "params": {"column": col, "method": "z_score"}})
        for col in categorical_cols[:2]:
            steps.append({"transformation": "encode_categories", "params": {"column": col, "method": "one_hot"}})
            
    elif template_name == "Analytics Preparation":
        # Convert strings, lowercase, rename/trim
        for col in categorical_cols[:2]:
            steps.append({"transformation": "lowercase", "params": {"column": col}})
            
    return steps
