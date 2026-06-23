import polars as pl
from app.services.semantic_detector import detect_semantic_type

def detect_outliers(df):
    outlier_issues = []

    for column in df.columns:
        col_lower = column.lower()

        # Get semantic type to determine skips/only-detects
        values_sample = df[column].drop_nulls().head(20).to_list()
        sem = detect_semantic_type(column, values_sample)
        semantic_type = sem.get("semantic_type", "UNKNOWN")

        # Skip ID, Text, Category, URL, and Name columns
        if (
            "id" in col_lower
            or "name" in col_lower
            or "email" in col_lower
            or "url" in col_lower
            or "link" in col_lower
            or "category" in col_lower
            or "industry" in col_lower
            or "gender" in col_lower
            or "text" in col_lower
            or "desc" in col_lower
            or "title" in col_lower
            or semantic_type in ["ID", "TEXT", "CATEGORY", "URL", "PERSON", "EMAIL"]
        ):
            continue

        # Outliers detect ONLY for Age, Price, Salary, Revenue, Payment, Weight, Numeric measures
        is_target = (
            "age" in col_lower
            or "price" in col_lower
            or "salary" in col_lower
            or "revenue" in col_lower
            or "payment" in col_lower
            or "amount" in col_lower
            or "cost" in col_lower
            or "fee" in col_lower
            or "weight" in col_lower
            or "measure" in col_lower
            or semantic_type in ["AGE", "PRICE", "MEASUREMENT", "COUNT", "RATING", "DURATION"]
        )
        if not is_target:
            continue

        try:
            dtype = df[column].dtype

            # Only run on actual numeric data types
            if dtype not in [
                pl.Int8, pl.Int16, pl.Int32, pl.Int64,
                pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                pl.Float32, pl.Float64
            ]:
                continue

            numeric_series = (
                df[column]
                .cast(pl.Float64, strict=False)
                .drop_nulls()
            )

            if len(numeric_series) < 5:
                continue

            q1 = numeric_series.quantile(0.25)
            q3 = numeric_series.quantile(0.75)

            if q1 is None or q3 is None:
                continue

            iqr = q3 - q1

            if iqr == 0:
                continue

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outlier_values = numeric_series.filter(
                (numeric_series < lower_bound) | (numeric_series > upper_bound)
            )

            outlier_count = len(outlier_values)

            if outlier_count > 0:
                outlier_issues.append({
                    "column": column,
                    "issue_type": "outliers",
                    "count": int(outlier_count),
                    "severity": "medium",
                    "lower_bound": round(lower_bound, 2),
                    "upper_bound": round(upper_bound, 2),
                    "sample_values": outlier_values.head(5).to_list()
                })

        except Exception as e:
            print(f"Outlier Detection Error in {column}: {e}")

    return outlier_issues