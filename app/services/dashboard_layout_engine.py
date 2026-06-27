from typing import Any, Dict, List

def build_layout(domain: str, kpis: List[Dict[str, Any]], charts: List[Dict[str, Any]], sections: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    """Groups KPIs and charts into logical dashboard pages based on domain and priority."""
    if sections is None:
        from app.services.dashboard_recommender import recommend_dashboard_sections
        cols = list(set([k.get("column") for k in kpis if k.get("column")] + 
                        [c.get("x_axis") for c in charts if c.get("x_axis")] + 
                        [c.get("y_axis") for c in charts if c.get("y_axis")]))
        schema = [{"column_name": col} for col in cols]
        sections = recommend_dashboard_sections(domain, schema)

    pages = []
    assigned_kpis = set()
    assigned_charts = set()

    for sec in sections:
        sec_name = sec["name"]
        sec_desc = sec["description"]
        
        page_kpis = []
        page_charts = []
        
        name_lower = sec_name.lower()
        
        if name_lower == "overview":
            # Overview shows High priority widgets
            page_kpis = [k for k in kpis if k.get("priority", "Medium") == "High"][:4]
            if not page_kpis:
                page_kpis = kpis[:3]
            page_charts = [c for c in charts if c.get("priority", "Medium") == "High"][:2]
            if not page_charts:
                page_charts = charts[:2]
        else:
            # Match based on keywords
            is_finance_page = any(k in name_lower for k in ["revenue", "sales", "financial", "salary", "compensation"])
            is_audience_page = any(k in name_lower for k in ["demographics", "audience", "customer", "workforce", "student", "patient", "employee"])
            is_item_page = any(k in name_lower for k in ["product", "course", "disease", "inventory", "catalog", "diagnoses"])
            is_time_page = any(k in name_lower for k in ["trends", "history", "time"])
            is_stats_page = any(k in name_lower for k in ["statistical", "distribution", "outliers"])

            # Filter unassigned KPIs
            for k in kpis:
                k_id = id(k)
                if k_id in assigned_kpis:
                    continue
                col_name = str(k.get("column") or "").lower()
                title = k.get("title") or k.get("name") or ""
                title = title.lower()
                
                matched = False
                if is_finance_page and any(kw in col_name or kw in title for kw in ["price", "amount", "cost", "revenue", "sales", "profit", "salary", "wage", "compensation", "income"]):
                    matched = True
                elif is_audience_page and any(kw in col_name or kw in title for kw in ["customer", "client", "user", "visitor", "employee", "student", "patient", "member", "subscriber", "staff", "worker", "age", "gender"]):
                    matched = True
                elif is_item_page and any(kw in col_name or kw in title for kw in ["product", "item", "brand", "course", "class", "subject", "disease", "illness", "diagnosis", "symptom"]):
                    matched = True
                elif is_time_page and any(kw in col_name or kw in title for kw in ["date", "time", "year", "month", "day"]):
                    matched = True
                
                if matched:
                    page_kpis.append(k)
                    assigned_kpis.add(k_id)

            # Filter unassigned charts
            for c in charts:
                c_id = id(c)
                if c_id in assigned_charts:
                    continue
                col_x = str(c.get("x_axis") or "").lower()
                col_y = str(c.get("y_axis") or "").lower()
                title = (c.get("title") or "").lower()
                c_type = (c.get("chart_type") or "").lower()
                
                matched = False
                if is_finance_page and any(kw in col_x or kw in col_y or kw in title for kw in ["price", "amount", "cost", "revenue", "sales", "profit", "salary", "wage", "compensation", "income"]):
                    matched = True
                elif is_audience_page and any(kw in col_x or kw in col_y or kw in title for kw in ["customer", "client", "user", "visitor", "employee", "student", "patient", "member", "subscriber", "staff", "worker", "age", "gender"]):
                    matched = True
                elif is_item_page and any(kw in col_x or kw in col_y or kw in title for kw in ["product", "item", "brand", "course", "class", "subject", "disease", "illness", "diagnosis", "symptom"]):
                    matched = True
                elif is_time_page and (c_type == "line chart" or any(kw in col_x or kw in title for kw in ["date", "time", "year", "month", "day"])):
                    matched = True
                elif is_stats_page and c_type in ["histogram", "box plot", "scatter plot", "heatmap", "pie chart", "treemap"]:
                    matched = True
                
                if matched:
                    page_charts.append(c)
                    assigned_charts.add(c_id)

        pages.append({
            "page": sec_name,
            "description": sec_desc,
            "kpis": page_kpis,
            "charts": page_charts
        })

    # leftover distribution
    leftover_kpis = [k for k in kpis if id(k) not in assigned_kpis]
    leftover_charts = [c for c in charts if id(c) not in assigned_charts]
    
    for k in leftover_kpis:
        if len(pages) > 1:
            pages[1]["kpis"].append(k)
        else:
            pages[0]["kpis"].append(k)
            
    for c in leftover_charts:
        c_type = c.get("chart_type", "").lower()
        stats_page = next((p for p in pages if "statistical" in p["page"].lower()), None)
        if stats_page:
            stats_page["charts"].append(c)
        elif len(pages) > 1:
            pages[1]["charts"].append(c)
        else:
            pages[0]["charts"].append(c)

    return pages
