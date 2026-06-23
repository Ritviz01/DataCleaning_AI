def generate_dashboard_recommendations(dataset_type: str, df=None, schema=None) -> list:
    col_names = []
    if df is not None:
        col_names = [c.lower().strip() for c in df.columns]
    elif schema is not None:
        col_names = [col.get("column_name", "").lower().strip() for col in schema]
        
    recommendations = []
    
    # 1. Category / Industry charts
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

    # 2. Demographic charts
    if "age" in col_names:
        recommendations.append({
            "chart_name": "Age Distribution",
            "chart_type": "Histogram",
            "x_axis": "Age Groups",
            "y_axis": "Frequency",
            "description": "Displays the age demographics of enrolled students."
        })

    # 3. Course popularity
    if "course" in col_names:
        recommendations.append({
            "chart_name": "Course Popularity",
            "chart_type": "Horizontal Bar Chart",
            "x_axis": "Number of Enrolled Students",
            "y_axis": "Course Name",
            "description": "Ranks courses by the total number of student enrollments."
        })

    # 4. Enrollment Trends
    if any("date" in c or "enroll" in c for c in col_names):
        recommendations.append({
            "chart_name": "Enrollment Trends",
            "chart_type": "Line Chart",
            "x_axis": "Enrollment Date/Semester",
            "y_axis": "Student Count",
            "description": "Tracks student enrollments over time to show growth patterns."
        })

    # 5. Price-based charts
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

    # 6. Financial charts (only if revenue/sales exist)
    if any(c in col_names for c in ["revenue", "sales", "profit"]):
        recommendations.append({
            "chart_name": "Sales Analysis",
            "chart_type": "Bar Chart",
            "x_axis": "Category",
            "y_axis": "Sales",
            "description": "Compares sales across categories."
        })
        
    return recommendations
