from app.services.validators import (
    is_valid_email,
    is_valid_date
)


def detect_issues(df):

    # Saare detected issues yahan store honge
    issues = []

    # Dataset ki total rows
    total_rows = df.height

    # -----------------------------------
    # Missing Values Detection
    # -----------------------------------

    for column in df.columns:

        null_count = df[column].null_count()

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

    duplicate_rows = (
        total_rows -
        df.unique().height
    )

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

        if "id" in column.lower():

            total_ids = (
                df[column]
                .drop_nulls()
                .len()
            )

            unique_ids = (
                df[column]
                .drop_nulls()
                .n_unique()
            )

            duplicate_ids = (
                total_ids -
                unique_ids
            )

            if duplicate_ids > 0:

                issues.append({
                    "column": column,
                    "issue_type": "duplicate_ids",
                    "count": int(duplicate_ids),
                    "severity": "high"
                })

    # -----------------------------------
    # Invalid Email Detection
    # -----------------------------------

    for column in df.columns:

        if "email" in column.lower():

            invalid_count = 0

            for value in df[column]:

                if value is None:
                    continue

                if not is_valid_email(value):
                    print(
                        'Invalid Email Found:',
                        repr(value)
                    )
                    invalid_count += 1

            if invalid_count > 0:

                issues.append({
                    "column": column,
                    "issue_type": "invalid_email",
                    "count": invalid_count,
                    "severity": "high"
                })

    # -----------------------------------
    # Invalid Date Detection
    # -----------------------------------

    for column in df.columns:

        if (
            "date" in column.lower()
            or "dob" in column.lower()
        ):

            invalid_count = 0

            for value in df[column]:

                if value is None:
                    continue

                if not is_valid_date(value):
                    print('Invalid Date Found:', repr(value))
                    invalid_count += 1

            if invalid_count > 0:

                issues.append({
                    "column": column,
                    "issue_type": "invalid_date",
                    "count": invalid_count,
                    "severity": "high"
                })

    return issues