def generate_recommendations(
    issues,
    schema,
    type_suggestions
):

    recommendations = []

    # Fast lookup for inferred types
    type_map = {
        item["column"]: item["suggested_type"]
        for item in type_suggestions
    }

    for issue in issues:

        column_name = issue["column"]

        column_schema = next(
            (
                col
                for col in schema
                if col["column_name"] == column_name
            ),
            None
        )

        if not column_schema:
            continue

        semantic_type = column_schema.get(
            "semantic_type",
            "UNKNOWN"
        )

        issue_type = issue["issue_type"]

        # ==================================
        # MISSING VALUES
        # ==================================

        if issue_type == "missing_values":

            percentage = issue.get(
                "percentage",
                0
            )

            suggested_type = type_map.get(
                column_name
            )

            # 100% missing column
            if percentage >= 100:

                recommendations.append({
                    "column": column_name,
                    "issue": "missing_values",
                    "recommended_action": "drop_column",
                    "reason": "Column contains 100% missing values",
                    "confidence": 1.0
                })

                continue

            # Numeric columns
            if suggested_type in ["Integer", "Float"]:

                recommendations.append({
                    "column": column_name,
                    "issue": "missing_values",
                    "recommended_action": "median_imputation",
                    "reason": "Numeric column detected by type inference",
                    "confidence": 0.95
                })

                continue

            # ID column
            if semantic_type == "ID":

                recommendations.append({
                    "column": column_name,
                    "issue": "missing_values",
                    "recommended_action": "manual_review",
                    "reason": "Primary identifier column",
                    "confidence": 0.95
                })

            # Date column
            elif semantic_type == "DATE":

                recommendations.append({
                    "column": column_name,
                    "issue": "missing_values",
                    "recommended_action": "forward_fill",
                    "reason": "Date column",
                    "confidence": 0.85
                })

            # Long text columns
            elif semantic_type in [
                "TEXT",
                "DESCRIPTION",
                "PARAGRAPH"
            ]:

                recommendations.append({
                    "column": column_name,
                    "issue": "missing_values",
                    "recommended_action": "leave_missing",
                    "reason": "Long text fields should not be mode imputed",
                    "confidence": 0.95
                })

            # URL columns
            elif semantic_type == "URL":

                recommendations.append({
                    "column": column_name,
                    "issue": "missing_values",
                    "recommended_action": "leave_missing",
                    "reason": "URLs should not be mode imputed",
                    "confidence": 0.95
                })

            # Default categorical handling
            else:

                recommendations.append({
                    "column": column_name,
                    "issue": "missing_values",
                    "recommended_action": "mode_imputation",
                    "reason": "Categorical column",
                    "confidence": 0.80
                })

        # ==================================
        # DUPLICATE ROWS
        # ==================================

        elif issue_type == "duplicate_rows":

            recommendations.append({
                "column": "ALL",
                "issue": "duplicate_rows",
                "recommended_action": "remove_duplicates",
                "reason": "Duplicate records detected",
                "confidence": 0.98
            })

        # ==================================
        # DUPLICATE IDS
        # ==================================

        elif issue_type == "duplicate_ids":

            recommendations.append({
                "column": column_name,
                "issue": "duplicate_ids",
                "recommended_action": "manual_review",
                "reason": "Primary key contains duplicates",
                "confidence": 1.0
            })

        # ==================================
        # OUTLIERS
        # ==================================

        elif issue_type == "outliers":

            recommendations.append({
                "column": column_name,
                "issue": "outliers",
                "recommended_action": "cap_outliers",
                "reason": "Outliers detected using IQR method",
                "confidence": 0.90
            })
        
        elif issue["issue_type"] == "constant_column":

            recommendations.append({

                "column": column_name,

                "issue": "constant_column",

                "recommended_action":
                "drop_column",

                "reason":
                "Column contains only one unique value",

                "confidence": 0.98
        })

    return recommendations