import json
import os
from openai import OpenAI
from typing import Any, Dict, List

def generate_spec(
    schema: List[Dict[str, Any]],
    domain: str,
    local_kpis: List[Dict[str, Any]],
    local_charts: List[Dict[str, Any]],
    layout_pages: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Combines KPIs, charts, and layout into a single frontend-independent JSON object."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {
            "dashboard": {
                "title": f"{domain} Analysis Dashboard",
                "pages": layout_pages
            }
        }

    client = OpenAI(api_key=api_key)
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

    prompt = f"""You are a Principal Business Intelligence Architect. Your task is to design a complete, structured dashboard JSON specification for a dataset in the '{domain}' domain.

VALID KPI METRIC OPTIONS:
{local_kpis}

VALID VISUALIZATION RECOMMENDATIONS:
{local_charts}

PROPOSED PAGE LAYOUT STRUCTURE:
{layout_pages}

CRITICAL RULES:
1. ONLY select KPIs and charts from the lists of valid options provided above. NEVER invent or assume any columns, aggregations, or axes.
2. For each chart you include, write a compelling:
   - "reason": Why this chart was selected and how it supports business metrics.
   - "business_value": The expected value of having this visualization (e.g., actionable decisions it drives).
   - "insight": The expected visual insight (what to look for in the chart).
3. Assign a prioritization level to each widget ("High", "Medium", "Low").
4. Output must be a single, valid JSON object only. No markdown formatting.
5. The JSON response MUST match this exact structure:
{{
  "dashboard": {{
    "title": "A descriptive, professional title for the dashboard",
    "pages": [
      {{
        "page": "Overview",
        "description": "Short description of the page purpose",
        "kpis": [
          {{
            "name": "Total Revenue",
            "column": "Price",
            "aggregation": "sum",
            "priority": "High"
          }}
        ],
        "charts": [
          {{
            "chart_type": "Bar Chart",
            "title": "Average Price by Company",
            "x_axis": "Company",
            "y_axis": "Price",
            "aggregation": "mean",
            "priority": "High",
            "reason": "...",
            "business_value": "...",
            "insight": "..."
          }}
        ]
      }}
    ]
  }}
}}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a dashboard layout and BI specification designer. You output raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
            
        data = json.loads(content)
        if "dashboard" not in data:
            data = {"dashboard": data}
        return data
    except Exception as e:
        print(f"Error calling OpenAI in dashboard spec generation: {e}. Falling back to default layout.")
        return {
            "dashboard": {
                "title": f"{domain} Performance Dashboard",
                "pages": layout_pages
            }
        }
