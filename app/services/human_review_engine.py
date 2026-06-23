def generate_review_flags(issues: list[dict], schema: list[dict]) -> list[dict]:
    flags = []
    
    for issue in issues:
        column = issue.get("column", "")
        issue_type = issue.get("issue_type", "")
        count = issue.get("count", 0)
        
        if issue_type == "duplicate_ids":
            flags.append({
                "column": column,
                "reason": f"{count} duplicate ids detected. IDs must be unique identifiers."
            })
        elif issue_type == "constant_column":
            flags.append({
                "column": column,
                "reason": f"Column contains only one unique value. Categorization might be static/invalid."
            })
        elif issue_type == "invalid_email":
            flags.append({
                "column": column,
                "reason": f"{count} invalid email formats detected. Manual verification recommended."
            })
        elif issue_type == "invalid_date":
            flags.append({
                "column": column,
                "reason": f"{count} invalid dates detected. Verify dates manually to ensure correct chronological sequence."
            })
        elif issue_type == "outliers" and count > 10:
            flags.append({
                "column": column,
                "reason": f"High volume of suspicious outliers ({count} records). Capping should be manually reviewed."
            })
            
    return flags
