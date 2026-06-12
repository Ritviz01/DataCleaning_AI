def detect_issues(df):

    # Saare detected issues yahan store honge
    issues = []

    # Dataset ki total rows
    total_rows = df.height

    # Har column ko check karo
    for column in df.columns:

        # Is column mein kitne null values hain
        null_count = df[column].null_count()

        # Agar null values hain toh issue add karo
        if null_count > 0:

            issues.append({
                "column": column,
                "issue_type": "missing_values",
                "count": null_count,
                "percentage": round(
                    (null_count / total_rows) * 100,
                    2
                ),
                "severity": "medium"
            })

    # Duplicate rows detect karo
    duplicate_rows = total_rows - df.unique().height

    # Agar duplicate rows mili
    if duplicate_rows > 0:

        issues.append({
            "column": "ALL",
            "issue_type": "duplicate_rows",
            "count": duplicate_rows,
            "severity": "high"
        })

    return issues