def generate_recommendations(
    issues,
    schema,
    type_suggestions
):

    recommendations = []

    type_map = {}

    for item in type_suggestions:
        type_map[item["column"]] = item["suggested_type"]

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

        # ==========================
        # MISSING VALUES
        # ==========================

        if issue["issue_type"] == "missing_values":

            percentage = issue.get(
                "percentage",
                0
            )

            suggested_type = type_map.get(
                column_name
            )

            # --------------------------
            # Entire Column Missing
            # --------------------------

            if percentage >= 100:

                recommendations.append({

                    "column": column_name,

                    "issue": "missing_values",

                    "recommended_action":
                        "drop_column",

                    "reason":
                        "Column contains 100% missing values",

                    "confidence": 1.0
                })

                continue

            # --------------------------
            # Numeric Columns
            # --------------------------

            if suggested_type in [
                "Integer",
                "Float"
            ]:

                recommendations.append({

                    "column": column_name,

                    "issue": "missing_values",

                    "recommended_action":
                        "median_imputation",

                    "reason":
                        "Numeric column detected by type inference",

                    "confidence": 0.95
                })

                continue

            # --------------------------
            # ID Columns
            # --------------------------

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

            # --------------------------
            # Date Columns
            # --------------------------

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

            # --------------------------
            # Text Columns
            # --------------------------

            elif semantic_type in [
                "TEXT",
                "DESCRIPTION",
                "PARAGRAPH"
            ]:

                recommendations.append({

                    "column": column_name,

                    "issue": "missing_values",

                    "recommended_action":
                        "leave_missing",

                    "reason":
                        "Long text fields should not be mode imputed",

                    "confidence": 0.95
                })

            # --------------------------
            # Categorical Columns
            # --------------------------

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

        # ==========================
        # DUPLICATE ROWS
        # ==========================

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

        # ==========================
        # DUPLICATE IDS
        # ==========================

        elif issue["issue_type"] == "duplicate_ids":

            recommendations.append({

                "column": column_name,

                "issue": "duplicate_ids",

                "recommended_action":
                    "manual_review",

                "reason":
                    "Primary key contains duplicates",

                "confidence": 1.0
            })

        # ==========================
        # OUTLIERS
        # ==========================

        elif issue["issue_type"] == "outliers":

            recommendations.append({

                "column": column_name,

                "issue": "outliers",

                "recommended_action":
                    "cap_outliers",

                "reason":
                    "Outliers detected using IQR method",

                "confidence": 0.90
            })

    return recommendations