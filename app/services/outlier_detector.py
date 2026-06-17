import polars as pl


# Columns jinke liye outlier detection skip karna hai
SKIP_OUTLIER_COLUMNS = [
    "duration",
    "weekly study"
]


def is_numeric_like(series, threshold=0.8):

    try:

        numeric_series = (
            series
            .cast(pl.String)
            .str.replace_all(r"[^0-9.-]", "")
            .cast(pl.Float64, strict=False)
        )

        valid_numeric = numeric_series.is_not_null().sum()

        confidence = valid_numeric / len(series)

        return confidence >= threshold

    except Exception:

        return False


def detect_outliers(df):

    outlier_issues = []

    for column in df.columns:

        # Skip ID columns
        if "id" in column.lower():
            continue

        # Skip predefined columns
        if column.lower() in SKIP_OUTLIER_COLUMNS:
            continue

        try:

            # Sirf numeric-like columns par kaam karo
            if not is_numeric_like(df[column]):
                continue

            numeric_series = (
                df[column]
                .cast(pl.String)
                .str.replace_all(r"[^0-9.-]", "")
                .cast(pl.Float64, strict=False)
                .drop_nulls()
            )

            if len(numeric_series) < 5:
                continue

            q1 = numeric_series.quantile(0.25)
            q3 = numeric_series.quantile(0.75)

            iqr = q3 - q1

            # Agar IQR zero hai toh skip
            if iqr == 0:
                continue

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outlier_values = numeric_series.filter(
                (numeric_series < lower_bound)
                |
                (numeric_series > upper_bound)
            )

            outlier_count = len(outlier_values)

            print(f"\nCOLUMN: {column}")
            print(f"Q1: {q1}")
            print(f"Q3: {q3}")
            print(f"IQR: {iqr}")
            print(f"LOWER: {lower_bound}")
            print(f"UPPER: {upper_bound}")
            print(f"OUTLIERS FOUND: {outlier_count}")

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

            print(
                f"Outlier Detection Error in {column}: {e}"
            )

    return outlier_issues