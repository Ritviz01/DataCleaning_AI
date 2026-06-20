import polars as pl

from app.services.type_converter import (
    apply_type_conversions
)


def auto_clean_dataset(
    df,
    recommendations,
    type_suggestions=None
):

    cleaned_df = df.clone()

    cleaning_log = []

    # ==========================================
    # Type Conversion
    # ==========================================

    if type_suggestions:

        try:

            cleaned_df = apply_type_conversions(
                cleaned_df,
                type_suggestions
            )

            cleaning_log.append({

                "action":
                "type_conversion",

                "columns_processed":
                len(type_suggestions)

            })

        except Exception as e:

            print(
                f"Type Conversion Error: {e}"
            )

    # ==========================================
    # Apply Recommendations
    # ==========================================

    for recommendation in recommendations:

        column = recommendation["column"]

        action = recommendation[
            "recommended_action"
        ]

        # ======================================
        # REMOVE DUPLICATES
        # ======================================

        if action == "remove_duplicates":

            try:

                before = cleaned_df.height

                cleaned_df = (
                    cleaned_df
                    .unique()
                )

                after = cleaned_df.height

                cleaning_log.append({

                    "action":
                    "remove_duplicates",

                    "rows_removed":
                    before - after

                })

            except Exception:

                pass

            continue

        # ======================================
        # Column Exists?
        # ======================================

        if column not in cleaned_df.columns:
            continue

        # ======================================
        # DROP COLUMN
        # ======================================

        if action == "drop_column":

            try:

                cleaned_df = (
                    cleaned_df
                    .drop(column)
                )

                cleaning_log.append({

                    "column":
                    column,

                    "action":
                    "drop_column"

                })

            except Exception:

                pass

        # ======================================
        # MEDIAN IMPUTATION
        # ======================================

        elif action == "median_imputation":

            try:

                median_value = (

                    cleaned_df[column]

                    .cast(
                        pl.Float64,
                        strict=False
                    )

                    .median()

                )

                cleaned_df = (
                    cleaned_df
                    .with_columns(

                        pl.col(column)

                        .cast(
                            pl.Float64,
                            strict=False
                        )

                        .fill_null(
                            median_value
                        )

                        .alias(column)

                    )
                )

                cleaning_log.append({

                    "column":
                    column,

                    "action":
                    "median_imputation",

                    "value_used":
                    median_value

                })

            except Exception:

                pass

        # ======================================
        # MODE IMPUTATION
        # ======================================

        elif action == "mode_imputation":

            try:

                mode_value = (

                    cleaned_df[column]

                    .drop_nulls()

                    .mode()

                )

                if len(mode_value) > 0:

                    mode_value = (
                        mode_value[0]
                    )

                    cleaned_df = (
                        cleaned_df
                        .with_columns(

                            pl.col(column)

                            .fill_null(
                                mode_value
                            )

                            .alias(column)

                        )
                    )

                    cleaning_log.append({

                        "column":
                        column,

                        "action":
                        "mode_imputation",

                        "value_used":
                        str(mode_value)

                    })

            except Exception:

                pass

        # ======================================
        # FORWARD FILL
        # ======================================

        elif action == "forward_fill":

            try:

                cleaned_df = (
                    cleaned_df
                    .with_columns(

                        pl.col(column)

                        .forward_fill()

                        .alias(column)

                    )
                )

                cleaning_log.append({

                    "column":
                    column,

                    "action":
                    "forward_fill"

                })

            except Exception:

                pass

        # ======================================
        # OUTLIER CAPPING
        # ======================================

        elif action == "cap_outliers":

            try:

                numeric_series = (

                    cleaned_df[column]

                    .cast(
                        pl.Float64,
                        strict=False
                    )

                    .drop_nulls()

                )

                if len(numeric_series) < 5:
                    continue

                q1 = (
                    numeric_series
                    .quantile(0.25)
                )

                q3 = (
                    numeric_series
                    .quantile(0.75)
                )

                if q1 is None or q3 is None:
                    continue

                iqr = q3 - q1

                if iqr == 0:
                    continue

                lower_bound = (
                    q1 -
                    (1.5 * iqr)
                )

                upper_bound = (
                    q3 +
                    (1.5 * iqr)
                )

                cleaned_df = (
                    cleaned_df
                    .with_columns(

                        pl.col(column)

                        .cast(
                            pl.Float64,
                            strict=False
                        )

                        .clip(
                            lower_bound,
                            upper_bound
                        )

                        .alias(column)

                    )
                )

                cleaning_log.append({

                    "column":
                    column,

                    "action":
                    "cap_outliers",

                    "lower_bound":
                    round(
                        lower_bound,
                        2
                    ),

                    "upper_bound":
                    round(
                        upper_bound,
                        2
                    )

                })

            except Exception:

                pass

    return (
        cleaned_df,
        cleaning_log
    )
