def detect_issues(df):

    # Saare detected issues yahan store honge
    issues = []

    # Dataset ki total rows
    total_rows = df.height

    # -----------------------------------
    # Missing Values Detection
    # -----------------------------------

    for column in df.columns:

        # Count null values
        null_count = df[column].null_count()

        # Agar null values hain
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

    # -----------------------------------
    # Duplicate Row Detection
    # -----------------------------------

    # Unique rows count compare karo
    duplicate_rows = (
        total_rows -
        df.unique().height
    )

    # Agar duplicate rows hain
    if duplicate_rows > 0:

        issues.append({
            "column": "ALL",
            "issue_type": "duplicate_rows",
            "count": int(duplicate_rows),
            "severity": "high"
        })

    # -----------------------------------
    # Duplicate ID Detection
    # -----------------------------------

    for column in df.columns:

        # Sirf ID-like columns check karo
        if "id" in column.lower():

            # Null hata ke count lo
            total_ids = (
                df[column]
                .drop_nulls()
                .len()
            )

            # Unique IDs count
            unique_ids = (
                df[column]
                .drop_nulls()
                .n_unique()
            )

            # Duplicate IDs count
            duplicate_ids = (
                total_ids -
                unique_ids
            )

            # Agar duplicate IDs hain
            if duplicate_ids > 0:

                issues.append({
                    "column": column,
                    "issue_type": "duplicate_ids",
                    "count": int(duplicate_ids),
                    "severity": "high"
                })

    return issues