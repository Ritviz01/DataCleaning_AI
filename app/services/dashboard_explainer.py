import os
from openai import OpenAI
from typing import Any, Dict

def generate_explanation(spec: dict) -> dict:
    """Generates a professional business explanation and summary of the dashboard specification.
    
    Args:
        spec: The complete generated dashboard spec dictionary.
        
    Returns:
        Dictionary containing 'summary' and 'details' list of widget explanations.
    """
    title = spec.get("title", "Dashboard")
    pages = spec.get("pages", [])
    
    details = []
    all_kpis = []
    all_charts = []
    
    for page in pages:
        kpis = page.get("kpis", [])
        charts = page.get("charts", [])
        
        for k in kpis:
            all_kpis.append(k.get("name", "Metric"))
            
        for chart in charts:
            chart_title = chart.get("title", "Chart")
            all_charts.append(chart_title)
            
            kpi_supported = "General Record Count"
            if kpis:
                for k in kpis:
                    if k.get("column") == chart.get("y_axis") or k.get("column") == chart.get("x_axis"):
                        kpi_supported = k.get("name")
                        break
            
            details.append({
                "component": chart_title,
                "kpi_supported": kpi_supported,
                "business_value": chart.get("business_value", "Provides detailed category performance metrics."),
                "insight": chart.get("insight", "Compares trends and highlights outliers.")
            })
            
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
        model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
        prompt = f"""You are a senior Business Intelligence Explainer service.
Given the following dashboard layout:
- Title: {title}
- KPIs: {all_kpis}
- Charts: {all_charts}

Provide a concise, professional 2-3 sentence executive business summary of why this dashboard was created, the value it provides to executive decision-makers, and how it guides strategy.
"""
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional Business Intelligence Explainer. Output a concise summary paragraph."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            summary = response.choices[0].message.content.strip()
        except Exception:
            summary = f"The '{title}' dashboard provides a comprehensive performance view utilizing key metrics ({', '.join(all_kpis[:3])}) and visual trend charts to enable executive decisions."
    else:
        summary = f"The '{title}' dashboard provides a comprehensive performance view utilizing key metrics ({', '.join(all_kpis[:3])}) and visual trend charts to enable executive decisions."
        
    return {
        "summary": summary,
        "details": details
    }
