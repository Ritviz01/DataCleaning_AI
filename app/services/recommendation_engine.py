# Generate recommendations from issues
def generate_recommendations(issues, schema):

    # Store all recommendations
    recommendations = []

    # Check every detected issue
    for issue in issues:

        column_name = issue["column"]

        # Find column information from schema
        column_schema = next(
            (
                col
                for col in schema
                if col["column_name"] == column_name
            ),
            None
        )

        # If schema not found, skip
        if not column_schema:
            continue

        semantic_type = column_schema["semantic_type"]

        # -------------------------
        # Missing Values Handling
        # -------------------------

        if issue["issue_type"] == "missing_values":

            # ID columns should not be auto-filled
            if semantic_type == "ID":

                recommendations.append({
                    "column": column_name,
                    "issue": "missing_values",
                    "recommended_action": "manual_review",
                    "reason": "Primary identifier column",
                    "confidence": 0.95
                })

            # Date columns
            elif semantic_type == "DATE":

                recommendations.append({
                    "column": column_name,
                    "issue": "missing_values",
                    "recommended_action": "forward_fill",
                    "reason": "Date column",
                    "confidence": 0.85
                })

            # Everything else (temporary)
            else:

                recommendations.append({
                    "column": column_name,
                    "issue": "missing_values",
                    "recommended_action": "mode_imputation",
                    "reason": "Categorical column",
                    "confidence": 0.80
                })

        # -------------------------
        # Duplicate Rows Handling
        # -------------------------

        elif issue["issue_type"] == "duplicate_rows":

            recommendations.append({
                "column": "ALL",
                "issue": "duplicate_rows",
                "recommended_action": "remove_duplicates",
                "reason": "Duplicate records detected",
                "confidence": 0.98
            })

    return recommendations