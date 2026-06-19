import polars as pl


SKIP_OUTLIER_COLUMNS = [
    "duration",
    "weekly study"
]


def detect_outliers(df):

    outlier_issues = []

    for column in df.columns:

        col_lower = column.lower()

        # ---------------------------
        # Skip ID columns
        # ---------------------------

        if "id" in col_lower:
            continue

        if col_lower in SKIP_OUTLIER_COLUMNS:
            continue

        try:

            dtype = df[column].dtype

            # ----------------------------------
            # Only REAL Numeric Columns
            # ----------------------------------

            if dtype not in [

                pl.Int8,
                pl.Int16,
                pl.Int32,
                pl.Int64,

                pl.UInt8,
                pl.UInt16,
                pl.UInt32,
                pl.UInt64,

                pl.Float32,
                pl.Float64

            ]:
                continue

            numeric_series = (

                df[column]

                .cast(
                    pl.Float64,
                    strict=False
                )

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
                (numeric_series < lower_bound)
                |
                (numeric_series > upper_bound)
            )

            outlier_count = len(outlier_values)

            if outlier_count > 0:

                outlier_issues.append({

                    "column":
                    column,

                    "issue_type":
                    "outliers",

                    "count":
                    int(outlier_count),

                    "severity":
                    "medium",

                    "lower_bound":
                    round(lower_bound, 2),

                    "upper_bound":
                    round(upper_bound, 2),

                    "sample_values":
                    outlier_values.head(5).to_list()

                })

        except Exception as e:

            print(
                f"Outlier Detection Error in {column}: {e}"
            )

    return outlier_issues