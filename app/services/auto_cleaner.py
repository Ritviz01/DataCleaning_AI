import polars as pl


def auto_clean_dataset(
    df,
    recommendations
):

    cleaned_df = df.clone()

    cleaning_log = []

    # ==========================================
    # Currency Cleanup (Optional)
    # ==========================================

    if "Total_Payments" in cleaned_df.columns:

        try:

            cleaned_df = cleaned_df.with_columns(

                pl.col("Total_Payments")

                .cast(pl.Utf8)

                .str.replace_all(
                    r"[^0-9.]",
                    ""
                )

                .cast(
                    pl.Float64,
                    strict=False
                )

                .alias(
                    "Total_Payments"
                )

            )

            cleaning_log.append({

                "column":
                "Total_Payments",

                "action":
                "currency_cleanup"

            })

        except Exception:

            pass

    # ==========================================
    # Apply Recommendations
    # ==========================================

    for recommendation in recommendations:

        column = recommendation["column"]

        action = recommendation[
            "recommended_action"
        ]

        # --------------------------------------
        # REMOVE DUPLICATES
        # --------------------------------------

        if action == "remove_duplicates":

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

            continue

        # --------------------------------------
        # Skip if column not exists
        # --------------------------------------

        if column not in cleaned_df.columns:
            continue

        # --------------------------------------
        # DROP COLUMN
        # --------------------------------------

        if action == "drop_column":

            cleaned_df = cleaned_df.drop(
                column
            )

            cleaning_log.append({

                "column":
                column,

                "action":
                "drop_column"

            })

        # --------------------------------------
        # MEDIAN IMPUTATION
        # --------------------------------------

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

                        .alias(
                            column
                        )

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

        # --------------------------------------
        # MODE IMPUTATION
        # --------------------------------------

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

                            .alias(
                                column
                            )

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

        # --------------------------------------
        # FORWARD FILL
        # --------------------------------------

        elif action == "forward_fill":

            try:

                cleaned_df = (
                    cleaned_df
                    .with_columns(

                        pl.col(column)

                        .forward_fill()

                        .alias(
                            column
                        )

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

        # --------------------------------------
        # CAP OUTLIERS
        # --------------------------------------

        elif action == "cap_outliers":

            try:

                numeric_col = (

                    cleaned_df[column]

                    .cast(
                        pl.Float64,
                        strict=False
                    )

                )

                q1 = (
                    numeric_col
                    .quantile(0.25)
                )

                q3 = (
                    numeric_col
                    .quantile(0.75)
                )

                iqr = q3 - q1

                lower_bound = (
                    q1 -
                    1.5 * iqr
                )

                upper_bound = (
                    q3 +
                    1.5 * iqr
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

                        .alias(
                            column
                        )

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