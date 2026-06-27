from collections import Counter
import polars as pl
from app.services.business_insight_engine import generate_business_context
from app.services.dashboard_recommender import generate_dashboard_recommendations

def generate_dataset_insights(df: pl.DataFrame, schema: list, metadata: dict, quality: dict, issues: list, domain: str = None) -> dict:
    rows_count = metadata.get("rows", 0)
    cols_count = metadata.get("columns", 0)
    
    # Check if dataset is too small or lacks info
    if rows_count < 3 or cols_count == 0:
        return {
            "summary": f"Dataset contains {rows_count} rows and {cols_count} columns.",
            "quality_analysis": f"Quality Score: {quality.get('quality_score', 0)} ({quality.get('grade', 'N/A')})",
            "major_issues": [],
            "semantic_distribution": {},
            "dashboard_suggestions": [],
            "business_insights": ["This dataset does not contain enough information to generate advanced business insights."],
            "recommended_kpis": []
        }
        
    # 1. Determine dataset type, business context, and KPIs
    biz_context = generate_business_context(df, schema, domain=domain)
    dataset_type = biz_context["dataset_type"]
    business_insights = [biz_context["business_context"]]
    recommended_kpis = biz_context["recommended_kpis"]
    
    # 2. Get dashboard recommendations
    dash_recs = generate_dashboard_recommendations(dataset_type, df, schema)
    dashboard_suggestions = [rec["chart_name"] for rec in dash_recs]
    
    # 3. Quality summary strings
    summary = f"Dataset contains {rows_count} rows and {cols_count} columns."
    quality_analysis = f"Quality Score: {quality.get('quality_score', 0)} ({quality.get('grade', 'N/A')})"
    
    # 4. Filter major high severity issues
    major_issues = []
    for issue in issues:
        if issue.get("severity") == "high":
            major_issues.append({
                "column": issue.get("column"),
                "issue": issue.get("issue_type")
            })
            
    # 5. Semantic distribution counts
    semantic_types = [col.get("semantic_type", "UNKNOWN") for col in schema]
    semantic_distribution = dict(Counter(semantic_types))
    
    return {
        "summary": summary,
        "quality_analysis": quality_analysis,
        "major_issues": major_issues,
        "semantic_distribution": semantic_distribution,
        "dashboard_suggestions": dashboard_suggestions,
        "business_insights": business_insights,
        "recommended_kpis": recommended_kpis
    }
