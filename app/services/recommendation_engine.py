# Generate recommendations using:
# 1. Detected issues
# 2. Schema information
# 3. Type inference suggestions

def generate_recommendations(
    issues,
    schema,
    type_suggestions
):

    # Store all recommendations
    recommendations = []

    # Fast lookup dictionary
    # Example:
    # {
    #   "Age": "Integer",
    #   "Total_Payments": "Float"
    # }
    type_map = {}

    for item in type_suggestions:

        type_map[item["column"]] = item["suggested_type"]

    # Check every detected issue
    for issue in issues:

        column_name = issue["column"]

        # Find schema information for current column
        column_schema = next(
            (
                col
                for col in schema
                if col["column_name"] == column_name
            ),
            None
        )

        # Skip if schema not found
        if not column_schema:
            continue

        semantic_type = column_schema["semantic_type"]

        # ----------------------------------
        # Missing Values Handling
        # ----------------------------------

        if issue["issue_type"] == "missing_values":

            # Get inferred datatype
            suggested_type = type_map.get(column_name)

            # ----------------------------------
            # Numeric Columns
            # Example:
            # Age
            # Salary
            # Revenue
            # Total_Payments
            # ----------------------------------

            if suggested_type in ["Integer", "Float"]:

                recommendations.append({

                    "column": column_name,

                    "issue": "missing_values",

                    "recommended_action":
                        "median_imputation",

                    "reason":
                        "Numeric column detected by type inference",

                    "confidence": 0.95
                })

                # Stop further processing
                continue

            # ----------------------------------
            # ID Columns
            # ----------------------------------

            if semantic_type == "ID":

                recommendations.append({

                    "column": column_name,

                    "issue": "missing_values",

                    "recommended_action":
                        "manual_review",

                    "reason":
                        "Primary identifier column",

                    "confidence": 0.95
                })

            # ----------------------------------
            # Date Columns
            # ----------------------------------

            elif semantic_type == "DATE":

                recommendations.append({

                    "column": column_name,

                    "issue": "missing_values",

                    "recommended_action":
                        "forward_fill",

                    "reason":
                        "Date column",

                    "confidence": 0.85
                })

            # ----------------------------------
            # Categorical Columns
            # ----------------------------------

            else:

                recommendations.append({

                    "column": column_name,

                    "issue": "missing_values",

                    "recommended_action":
                        "mode_imputation",

                    "reason":
                        "Categorical column",

                    "confidence": 0.80
                })

        # ----------------------------------
        # Duplicate Rows Handling
        # ----------------------------------

        elif issue["issue_type"] == "duplicate_rows":

            recommendations.append({

                "column": "ALL",

                "issue": "duplicate_rows",

                "recommended_action":
                    "remove_duplicates",

                "reason":
                    "Duplicate records detected",

                "confidence": 0.98
            })

    return recommendations