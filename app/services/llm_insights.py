from collections import Counter


def generate_llm_insights(
    metadata,
    quality,
    issues,
    schema
):

    insights = {}

    # =========================
    # Dataset Summary
    # =========================

    insights["summary"] = (

        f"Dataset contains "
        f"{metadata['rows']} rows and "
        f"{metadata['columns']} columns."

    )

    # =========================
    # Quality Analysis
    # =========================

    insights["quality_analysis"] = (

        f"Quality Score: "
        f"{quality['quality_score']} "
        f"({quality['grade']})"

    )

    # =========================
    # Major Issues
    # =========================

    major_issues = []

    for issue in issues:

        if issue["severity"] == "high":

            major_issues.append({

                "column":
                issue["column"],

                "issue":
                issue["issue_type"]

            })

    insights["major_issues"] = major_issues

    # =========================
    # Column Type Distribution
    # =========================

    semantic_types = [

        col["semantic_type"]

        for col in schema

    ]

    insights[
        "semantic_distribution"
    ] = dict(

        Counter(
            semantic_types
        )

    )

    # =========================
    # Dashboard Suggestions
    # =========================

    dashboard_suggestions = []

    if "PRICE" in semantic_types:

        dashboard_suggestions.append(
            "Price Distribution Histogram"
        )

    if "CATEGORY" in semantic_types:

        dashboard_suggestions.append(
            "Category Wise Count Chart"
        )

    if "DATE" in semantic_types:

        dashboard_suggestions.append(
            "Time Series Trend"
        )

    insights[
        "dashboard_suggestions"
    ] = dashboard_suggestions

    return insights