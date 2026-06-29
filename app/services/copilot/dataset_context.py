import polars as pl
from typing import Dict, Any

def build_dataset_context(df: pl.DataFrame) -> Dict[str, Any]:
    """
    Builds a compact context representation of a dataset without raw rows or sensitive information.
    Includes metadata, schema, semantic types, profile summaries, quality issues, and recommendations.
    """
    from app.services.pipeline import analyse_dataset
    from app.services.dataset_classifier import classify_dataset
    from app.services.kpi_generator import generate_kpis
    from app.services.chart_recommender import recommend_charts
    
    # 1. Run main analytics engine
    analysis = analyse_dataset(df)
    
    metadata = analysis.get("metadata", {})
    schema = analysis.get("schema", [])
    profile = analysis.get("profile", [])
    quality = analysis.get("quality", {})
    issues = analysis.get("issues", [])
    recommendations = analysis.get("recommendations", [])
    type_suggestions = analysis.get("type_suggestions", [])
    
    # 2. Extract profile summary (non-sensitive stats)
    profile_summary = []
    for col_p in profile:
        profile_summary.append({
            "column": col_p.get("column_name"),
            "null_count": col_p.get("null_count", 0),
            "null_percentage": col_p.get("null_percentage", 0.0),
            "distinct_values": col_p.get("unique_values", 0),
            "min": str(col_p.get("min")) if col_p.get("min") is not None else None,
            "max": str(col_p.get("max")) if col_p.get("max") is not None else None,
            "mean": round(col_p.get("mean"), 2) if isinstance(col_p.get("mean"), (int, float)) else None
        })
        
    # 3. Classify and get suggestions
    dataset_type = "General"
    kpis = []
    charts = []
    try:
        class_res = classify_dataset(metadata, metadata.get("column_names", []), schema)
        dataset_type = class_res.get("dataset_type", "General")
        kpis = generate_kpis(dataset_type, schema)
        charts = recommend_charts(schema)
    except Exception as e:
        print(f"Error classifying dataset for copilot context: {e}")
        
    return {
        "dataset_name": metadata.get("filename") or "dataset",
        "row_count": metadata.get("rows", 0),
        "column_count": metadata.get("columns", 0),
        "columns": [
            {
                "name": col.get("column_name"),
                "type": col.get("type"),
                "semantic_type": col.get("semantic_type")
            }
            for col in schema
        ],
        "profile_summary": profile_summary,
        "quality": {
            "score": quality.get("quality_score"),
            "grade": quality.get("grade"),
            "completeness": quality.get("sub_scores", {}).get("completeness"),
            "uniqueness": quality.get("sub_scores", {}).get("uniqueness"),
            "validity": quality.get("sub_scores", {}).get("validity")
        },
        "detected_issues": [
            {
                "column": issue.get("column"),
                "issue_type": issue.get("issue_type"),
                "count": issue.get("count"),
                "severity": issue.get("severity")
            }
            for issue in issues
        ],
        "recommendations": [
            {
                "column": rec.get("column"),
                "recommended_action": rec.get("recommended_action"),
                "reason": rec.get("reason")
            }
            for rec in recommendations
        ],
        "type_suggestions": [
            {
                "column": sug.get("column"),
                "current_type": sug.get("current_type"),
                "suggested_type": sug.get("suggested_type")
            }
            for sug in type_suggestions
        ],
        "dashboard_suggestions": {
            "dataset_type": dataset_type,
            "recommended_kpis": kpis if kpis else [],
            "recommended_charts": [c.get("chart") for c in charts] if charts else []
        }
    }
