# Regular expressions use karne ke liye
import re


# Better datatype infer karne ke liye
def infer_better_types(df, schema=None):

    # Suggestions store karenge
    suggestions = []

    # Har column check karo
    semantic_map = {item["column_name"]: item["semantic_type"] for item in (schema or [])}

    for column in df.columns:
        # Identifiers must remain strings: converting 00123 to 123 corrupts data.
        if semantic_map.get(column) in {"ID", "PHONE", "URL", "EMAIL"}:
            continue

        # Column ke first 50 non-null values lo
        sample_values = (
            df[column]
            .drop_nulls()
            .head(50)
            .to_list()
        )

        # Agar column empty hai to skip
        if not sample_values:
            continue

        total_values = len(sample_values)

        numeric_count = 0
        float_count = 0

        # Har sample value check karo
        for value in sample_values:

            value = str(value).strip()

            # Integer detect
            if value.isdigit():
                numeric_count += 1

            # Float detect
            try:
                float(value)
                float_count += 1
            except:
                pass

        # Integer-like column
        if numeric_count / total_values >= 0.8:

            suggestions.append({
                "column": column,
                "current_type": "String",
                "suggested_type": "Integer",
                "confidence": round(
                    numeric_count / total_values,
                    2
                )
            })

        # Float-like column
        elif float_count / total_values >= 0.8:

            suggestions.append({
                "column": column,
                "current_type": "String",
                "suggested_type": "Float",
                "confidence": round(
                    float_count / total_values,
                    2
                )
            })

    return suggestions
