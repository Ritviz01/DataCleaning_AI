import polars as pl


def auto_clean_dataset(
    df,
    recommendations
):

    # Cleaning log
    cleaning_log = []

    # Clone dataframe
    cleaned_df = df.clone()

    # ---------------------------------
    # Currency Cleanup
    # ---------------------------------

    if (
        "Total_Payments"
        in cleaned_df.columns
    ):

        try:

            cleaned_df = (
                cleaned_df
                .with_columns(

                    pl.col(
                        "Total_Payments"
                    )

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
            )

            cleaning_log.append({

                "column":
                    "Total_Payments",

                "action":
                    "currency_cleanup"

            })

        except Exception:

            pass

    # ---------------------------------
    # Process Recommendations
    # ---------------------------------

    for recommendation in recommendations:

        column = (
            recommendation[
                "column"
            ]
        )

        action = (
            recommendation[
                "recommended_action"
            ]
        )

        # Column exists?
        if (
            column
            not in cleaned_df.columns
        ):
            continue

        # ---------------------------------
        # MEDIAN IMPUTATION
        # ---------------------------------

        if (
            action
            ==
            "median_imputation"
        ):

            try:

                numeric_series = (

                    cleaned_df[column]

                    .cast(
                        pl.Float64,
                        strict=False
                    )

                )

                median_value = (
                    numeric_series
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

        # ---------------------------------
        # MODE IMPUTATION
        # ---------------------------------

        elif (
            action
            ==
            "mode_imputation"
        ):

            try:

                mode_value = (

                    cleaned_df[column]

                    .drop_nulls()

                    .mode()

                )

                if (
                    len(mode_value)
                    > 0
                ):

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
                            str(
                                mode_value
                            )

                    })

            except Exception:

                pass

        # ---------------------------------
        # FORWARD FILL
        # ---------------------------------

        elif (
            action
            ==
            "forward_fill"
        ):

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

    return (
        cleaned_df,
        cleaning_log
    )