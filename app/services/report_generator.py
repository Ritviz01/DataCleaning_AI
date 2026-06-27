import os
import json
from openai import OpenAI

from app.services.openai_service import sanitize_text

def generate_report_locally(
    metadata: dict,
    quality: dict,
    issues: list,
    kpis: list,
    charts: list,
    dataset_type: str,
    schema: list = None
) -> dict:
    issues_summary = [f"{len(issues)} data quality issues found."]
    if not issues:
        issues_summary = ["No high severity data quality issues detected."]
        
    report = {
        "executive_summary": f"This executive report covers the '{dataset_type}' dataset containing {metadata.get('rows', 0)} rows and {metadata.get('columns', 0)} columns.",
        "data_quality_summary": f"The overall dataset quality score is evaluated at {quality.get('quality_score', 0)} resulting in a grade of {quality.get('grade', 'N/A')}.",
        "major_issues": [f"{issue.get('issue_type', '')} in column '{issue.get('column', '')}'" for issue in issues[:3]] or issues_summary,
        "business_insights": [f"This {dataset_type} dataset profile supports operational metrics and dashboard reporting."],
        "recommended_actions": ["Perform the proposed automated data cleanups.", "Verify columns with invalid formats."],
        "suggested_kpis": kpis,
        "suggested_charts": [c.get("chart", "") for c in charts]
    }
    return sanitize_text(report, schema, metadata)

def generate_report(
    metadata: dict,
    quality: dict,
    issues: list,
    kpis: list,
    charts: list,
    dataset_type: str,
    schema: list = None
) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return generate_report_locally(metadata, quality, issues, kpis, charts, dataset_type, schema)
        
    client = OpenAI(api_key=api_key)
    
    prompt = f"""You are an Executive Business Analyst.
Generate a structured JSON executive business report for a dataset of type '{dataset_type}'.

Dataset Quality Metrics:
- Quality Score: {quality}
- Issues Count: {len(issues)}
- Proposed KPIs: {kpis}
- Proposed Charts: {charts}

Return your response in raw JSON format (no markdown code blocks, just raw JSON) containing exactly the following keys:
1. "executive_summary": "..."
2. "data_quality_summary": "..."
3. "major_issues": ["..."]
4. "business_insights": ["..."]
5. "recommended_actions": ["..."]
6. "suggested_kpis": ["..."]
7. "suggested_charts": ["..."]
"""
    try:
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[
                {"role": "system", "content": "You are an executive reporting system. Output raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        report = json.loads(content)
        return sanitize_text(report, schema, metadata)
    except Exception:
        return generate_report_locally(metadata, quality, issues, kpis, charts, dataset_type, schema)
