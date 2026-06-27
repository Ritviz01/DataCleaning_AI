def generate_review_flags(issues: list[dict], schema: list[dict], type_suggestions: list[dict] = None) -> list[dict]:
    flags = []
    
    # 1. Process issues
    for issue in issues:
        column = issue.get("column", "")
        issue_type = issue.get("issue_type", "")
        count = issue.get("count", 0)
        severity = issue.get("severity", "medium")
        
        reason = ""
        suggested_action = ""
        
        if issue_type == "duplicate_ids":
            reason = f"{count} duplicate ids detected. IDs must be unique identifiers."
            suggested_action = "Identify and remove duplicate records or generate unique IDs."
        elif issue_type == "constant_column":
            reason = "Column contains only one unique value. Categorization might be static/invalid."
            suggested_action = "Verify if this column is necessary or clean the source data."
        elif issue_type == "invalid_email":
            reason = f"{count} invalid email formats detected. Manual verification recommended."
            suggested_action = "Standardize email formatting or flag invalid addresses for review."
        elif issue_type == "invalid_date":
            reason = f"{count} invalid dates detected. Verify dates manually to ensure correct chronological sequence."
            suggested_action = "Reformat date values or investigate data entry pipeline."
        elif issue_type == "outliers":
            reason = f"High volume of suspicious outliers ({count} records). Capping should be manually reviewed."
            suggested_action = "Review the distribution and apply capping, outlier removal, or scaling."
        else:
            reason = f"Issue of type '{issue_type}' detected."
            suggested_action = "Examine the column data for clean-up."
            
        flags.append({
            "column": column,
            "severity": severity,
            "reason": reason,
            "suggested_action": suggested_action
        })
        
    # 2. Process schema (check if there is an ID column)
    has_id = any(col.get("semantic_type") == "ID" for col in schema)
    if schema and not has_id:
        flags.append({
            "column": "ALL",
            "severity": "low",
            "reason": "No primary identifier or ID column was detected in the dataset schema.",
            "suggested_action": "Designate a column as ID or generate a unique row identifier."
        })
        
    # 3. Process type suggestions
    if type_suggestions:
        for sug in type_suggestions:
            col = sug.get("column", "")
            curr = sug.get("current_type", "String")
            suggested = sug.get("suggested_type", "numeric")
            conf = sug.get("confidence", 1.0)
            
            flags.append({
                "column": col,
                "severity": "low",
                "reason": f"Column is currently read as {curr}, but over 80% of values match the format of {suggested} (confidence: {conf}).",
                "suggested_action": f"Cast column to {suggested} to optimize storage and allow mathematical analysis."
            })
            
    return flags
