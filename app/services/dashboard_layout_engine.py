from typing import Any, Dict, List

def build_layout(domain: str, kpis: List[Dict[str, Any]], charts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Groups KPIs and charts into logical dashboard pages based on domain and priority.
    
    Args:
        domain: Detected domain name.
        kpis: Calculated KPI dictionary objects.
        charts: Recommended chart specification objects.
        
    Returns:
        List of dashboard page dictionaries containing widgets.
    """
    pages = []
    
    # 1. Page: Overview
    overview_kpis = [k for k in kpis if k.get("priority") == "High"]
    if not overview_kpis:
        overview_kpis = kpis[:3]
        
    overview_charts = [c for c in charts if c.get("priority") == "High"]
    if not overview_charts:
        overview_charts = charts[:2]
        
    pages.append({
        "page": "Overview",
        "description": f"High-level overview of critical {domain} metrics and trends.",
        "kpis": overview_kpis,
        "charts": overview_charts
    })

    # 2. Page: Detailed Analysis
    detail_kpis = [k for k in kpis if k.get("priority") == "Medium"]
    detail_charts = [c for c in charts if c.get("priority") == "Medium"]
    if not detail_charts:
        # Fallback to next chunk of recommendations
        detail_charts = [c for c in charts if c not in overview_charts][:3]
        
    pages.append({
        "page": f"{domain} Performance" if domain != "General" else "Performance Analysis",
        "description": "Granular metrics and categorical distributions.",
        "kpis": detail_kpis,
        "charts": detail_charts
    })

    # 3. Page: Distribution & Correlation
    dist_kpis = [k for k in kpis if k.get("priority") == "Low"]
    dist_charts = [c for c in charts if c.get("priority") == "Low"]
    if not dist_charts:
        # Fallback to remaining charts
        used_charts = set(id(c) for c in (overview_charts + detail_charts))
        dist_charts = [c for c in charts if id(c) not in used_charts][:3]
        
    if dist_charts or dist_kpis:
        pages.append({
            "page": "Distribution & Correlation",
            "description": "Statistical distributions, correlation profiles, and range analysis.",
            "kpis": dist_kpis,
            "charts": dist_charts
        })
        
    # 4. Page: Executive Summary
    pages.append({
        "page": "Executive Summary",
        "description": "AI-generated executive summary, strategic recommendations, and potential business risks.",
        "kpis": [],
        "charts": []
    })

    return pages
