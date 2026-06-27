def recommend_dashboard_sections(domain: str, schema: list[dict]) -> list[dict]:
    """Determines which dashboard pages/sections should exist based on the dataset domain and column schema."""
    col_names = [col.get("column_name", "").lower().strip() for col in schema]
    
    sections = []
    
    # 1. Overview is always recommended
    sections.append({
        "name": "Overview",
        "description": f"High-level executive overview of the {domain} dataset."
    })
    
    # 2. Add domain-specific sections
    domain_lower = domain.lower()
    
    # Financial/Revenue/Salary Section
    has_finance = any(k in col_names for k in ["price", "amount", "cost", "revenue", "sales", "profit", "salary", "wage", "compensation", "income"])
    if has_finance:
        name = "Revenue & Sales" if domain_lower in ["sales", "ecommerce", "finance"] else "Financial Analysis"
        if domain_lower == "hr":
            name = "Salary & Compensation"
        sections.append({
            "name": name,
            "description": "Detailed financial performance and monetary metrics."
        })
        
    # Audience/Demographics Section
    has_audience = any(k in col_names for k in ["customer", "client", "employee", "student", "patient", "user", "visitor", "member", "subscriber", "staff", "worker", "age", "gender"])
    if has_audience:
        name = "Demographics"
        if domain_lower == "hr":
            name = "Workforce Demographics"
        elif domain_lower == "education":
            name = "Student Profiles"
        elif domain_lower == "healthcare":
            name = "Patient Demographics"
        elif domain_lower in ["sales", "ecommerce"]:
            name = "Customer Analysis"
        sections.append({
            "name": name,
            "description": "Analysis of profiles, demographics, and segments."
        })
        
    # Items/Products/Courses/Diseases Section
    has_items = any(k in col_names for k in ["product", "item", "brand", "course", "class", "subject", "disease", "illness", "diagnosis", "symptom"])
    if has_items:
        name = "Products & Inventory"
        if domain_lower == "education":
            name = "Course Catalog"
        elif domain_lower == "healthcare":
            name = "Diseases & Diagnoses"
        sections.append({
            "name": name,
            "description": "Detailed metrics per category or item type."
        })
        
    # Temporal Trends Section
    has_time = any(k in col_names for k in ["date", "time", "year", "month", "day", "timestamp", "created_at"])
    if has_time:
        sections.append({
            "name": "Trends & History",
            "description": "Visual history and trends over time."
        })
        
    # Fallback/General Page if no other pages were recommended
    if len(sections) == 1:
        sections.append({
            "name": "Performance Analysis",
            "description": "Analysis of key categories and categorical distributions."
        })
        
    # Distributions & Statistical Relationships Page
    sections.append({
        "name": "Statistical Distributions",
        "description": "Probability distributions, range analyses, and statistical outliers."
    })
    
    return sections


def generate_dashboard_recommendations(dataset_type: str, df=None, schema=None) -> list:
    """Legacy function to recommend charts for compatibility."""
    col_names = []
    if df is not None:
        col_names = [c.lower().strip() for c in df.columns]
    elif schema is not None:
        col_names = [col.get("column_name", "").lower().strip() for col in schema]
        
    recommendations = []
    
    if any("industry" in c or "category" in c for c in col_names) or dataset_type == "industry_lookup_dataset":
        recommendations.append({
            "chart_name": "Industry Distribution",
            "chart_type": "Pie Chart",
            "x_axis": "Industry",
            "y_axis": "Percentage",
            "description": "Visualizes the percentage share of each industry sector in the dataset."
        })
        recommendations.append({
            "chart_name": "Industry Frequency",
            "chart_type": "Bar Chart",
            "x_axis": "Industry",
            "y_axis": "Count",
            "description": "Shows the number of organizations in each industry sector."
        })
        recommendations.append({
            "chart_name": "Category Breakdown",
            "chart_type": "Donut Chart",
            "x_axis": "Category",
            "y_axis": "Count",
            "description": "Breakdown of category groups."
        })

    if "age" in col_names:
        recommendations.append({
            "chart_name": "Age Distribution",
            "chart_type": "Histogram",
            "x_axis": "Age Groups",
            "y_axis": "Frequency",
            "description": "Displays the age demographics of enrolled students."
        })

    if "course" in col_names:
        recommendations.append({
            "chart_name": "Course Popularity",
            "chart_type": "Horizontal Bar Chart",
            "x_axis": "Number of Enrolled Students",
            "y_axis": "Course Name",
            "description": "Ranks courses by the total number of student enrollments."
        })

    if any("date" in c or "enroll" in c for c in col_names):
        recommendations.append({
            "chart_name": "Enrollment Trends",
            "chart_type": "Line Chart",
            "x_axis": "Enrollment Date/Semester",
            "y_axis": "Student Count",
            "description": "Tracks student enrollments over time to show growth patterns."
        })

    has_price = any(c in col_names for c in ["price", "amount", "cost"])
    if has_price:
        price_col = next((c for c in col_names if c in ["price", "amount", "cost"]), "price")
        recommendations.append({
            "chart_name": "Price Distribution",
            "chart_type": "Histogram",
            "x_axis": "Price Range",
            "y_axis": "Frequency",
            "description": "Highlights the distribution of pricing tiers."
        })
        if any(c in col_names for c in ["company", "brand"]):
            recommendations.append({
                "chart_name": "Company Comparison",
                "chart_type": "Bar Chart",
                "x_axis": "Company/Brand",
                "y_axis": "Average Price",
                "description": "Compares average pricing across different manufacturers."
            })
        if "ram" in col_names:
            recommendations.append({
                "chart_name": "Price vs RAM",
                "chart_type": "Scatter Plot",
                "x_axis": "RAM (GB)",
                "y_axis": "Price",
                "description": "Analyzes the correlation between system memory size and retail price."
            })

    if any(c in col_names for c in ["revenue", "sales", "profit"]):
        recommendations.append({
            "chart_name": "Sales Analysis",
            "chart_type": "Bar Chart",
            "x_axis": "Category",
            "y_axis": "Sales",
            "description": "Compares sales across categories."
        })
        
    return recommendations
