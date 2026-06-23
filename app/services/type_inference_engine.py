import re
import polars as pl

def classify_value_type(val_str):
    val_str = val_str.strip()
    if not val_str:
        return None
    
    # 1. Clean Integer
    if re.match(r"^[-+]?\d+$", val_str):
        return "Integer"
        
    # 2. Clean Float
    if re.match(r"^[-+]?\d*\.\d+$", val_str):
        return "Float"
        
    # 3. Currency / Price indicators -> Float
    currency_stripped = re.sub(r"^\s*[\$€£¥]\s*|\s*[\$€£¥]\s*$", "", val_str).strip()
    if currency_stripped != val_str:
        if re.match(r"^[-+]?\d+(\.\d+)?$", currency_stripped):
            return "Float"
            
    # 4. Integer-like: contains digits only before a unit or letters (like 8GB)
    if re.match(r"^[-+]?\d+\s*[a-zA-Z]+$", val_str):
        return "Integer-like"
        
    # 5. Float-like: contains a decimal number before a unit or letters (like 2.5kg)
    if re.match(r"^[-+]?\d*\.\d+\s*[a-zA-Z]+$", val_str):
        return "Float-like"
        
    return None

def infer_better_types(df, schema=None):
    suggestions = []
    semantic_map = {item["column_name"]: item["semantic_type"] for item in (schema or [])}

    for column in df.columns:
        # Identifiers must remain strings: converting 00123 to 123 corrupts data.
        if semantic_map.get(column) in {"ID", "PHONE", "URL", "EMAIL"}:
            continue

        dtype = df[column].dtype
        # Skip if already a numerical/boolean type
        if dtype in [
            pl.Int8, pl.Int16, pl.Int32, pl.Int64,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
            pl.Float32, pl.Float64, pl.Boolean
        ]:
            continue

        sample_values = (
            df[column]
            .drop_nulls()
            .head(50)
            .to_list()
        )

        if not sample_values:
            continue

        total_values = len(sample_values)
        integer_cnt = 0
        float_cnt = 0
        integer_like_cnt = 0
        float_like_cnt = 0

        for value in sample_values:
            val_type = classify_value_type(str(value))
            if val_type == "Integer":
                integer_cnt += 1
            elif val_type == "Float":
                float_cnt += 1
            elif val_type == "Integer-like":
                integer_like_cnt += 1
            elif val_type == "Float-like":
                float_like_cnt += 1

        total_valid = integer_cnt + float_cnt + integer_like_cnt + float_like_cnt
        if total_valid / total_values >= 0.8:
            if (float_cnt + float_like_cnt) > 0:
                if float_like_cnt > 0:
                    suggested = "Float-like"
                else:
                    suggested = "Float"
                confidence = total_valid / total_values
            else:
                if integer_like_cnt > 0:
                    suggested = "Integer-like"
                else:
                    suggested = "Integer"
                confidence = total_valid / total_values

            suggestions.append({
                "column": column,
                "current_type": "String",
                "suggested_type": suggested,
                "confidence": round(confidence, 2)
            })

    return suggestions
