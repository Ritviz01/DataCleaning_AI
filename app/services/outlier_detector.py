import polars as pl


def detect_outliers(df):

    outlier_issues = []

    for column in df.columns:

        if 'id' in column.lower():
            continue

        try:

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
            print(f"OUTLIERS: {outlier_values.to_list()}")

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