def generate_kpis(dataset_type: str, schema: list[dict]) -> list[str]:
    col_names = [col.get("column_name", "").lower().strip() for col in schema]
    kpis = []
    
    domain = dataset_type.lower()
    
    if "education" in domain:
        kpis = ["Average Course Rating", "Total Enrollments", "Student Growth"]
        if "grade" in col_names or "gpa" in col_names:
            kpis.append("Average Grade / GPA")
        if "course_id" in col_names or "course" in col_names:
            kpis.append("Course Completion Rate")
            
    elif "ecommerce" in domain:
        kpis = ["Total Revenue", "Average Order Value", "Customer Retention"]
        if "quantity" in col_names:
            kpis.append("Total Units Sold")
            
    elif "sales" in domain:
        kpis = ["Total Sales Value", "Sales Growth Rate", "Average Order Size"]
        if "revenue" in col_names:
            kpis.append("Gross Margin")
            
    elif "hr" in domain:
        kpis = ["Employee Count", "Average Salary"]
        if "attrition" in col_names or "exit" in col_names:
            kpis.append("Attrition Rate")
            
    elif "finance" in domain:
        kpis = ["Total Net Profit", "Operating Expenses", "ROI"]
        
    elif "healthcare" in domain:
        kpis = ["Average Patient Stay", "Readmission Rate", "Patient Satisfaction Index"]
        
    elif "marketing" in domain:
        kpis = ["Conversion Rate", "Customer Acquisition Cost (CAC)", "Total Impressions"]
        
    else: # Fallbacks for general/CRM/logistics
        if any(c in col_names for c in ["price", "amount", "revenue"]):
            kpis.append("Total Transaction Value")
            kpis.append("Average Transaction Value")
        kpis.append("Record Count")
        
    return kpis
