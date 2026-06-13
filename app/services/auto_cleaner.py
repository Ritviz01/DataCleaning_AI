import polars as pl


# Apply recommendations and clean dataset
def auto_clean_dataset(df, recommendations):

    # Cleaning log maintain karenge
    cleaning_log = []

    # Copy dataframe
    # Original dataframe safe rahega
    cleaned_df = df.clone()

    # Process every recommendation
    for recommendation in recommendations:

        column = recommendation["column"]

        action = recommendation["recommended_action"]

        # Skip if column not found
        if column not in cleaned_df.columns:
            continue

        # -----------------------------
        # Median Imputation
        # -----------------------------

        if action == "median_imputation":

            try:

                # Convert column to numeric
                numeric_series = (
                    cleaned_df[column]
                    .cast(pl.Float64, strict=False)
                )

                # Calculate median
                median_value = numeric_series.median()

                # Fill missing values
                cleaned_df = cleaned_df.with_columns(
                    pl.col(column)
                    .cast(pl.Float64, strict=False)
                    .fill_null(median_value)
                    .alias(column)
                )

                cleaning_log.append({
                    "column": column,
                    "action": "median_imputation",
                    "value_used": median_value
                })

            except Exception:

                pass

        # -----------------------------
        # Mode Imputation
        # -----------------------------

        elif action == "mode_imputation":

            try:

                mode_value = (
                    cleaned_df[column]
                    .drop_nulls()
                    .mode()
                )

                if len(mode_value) > 0:

                    mode_value = mode_value[0]

                    cleaned_df = cleaned_df.with_columns(
                        pl.col(column)
                        .fill_null(mode_value)
                        .alias(column)
                    )

                    cleaning_log.append({
                        "column": column,
                        "action": "mode_imputation",
                        "value_used": str(mode_value)
                    })

            except Exception:

                pass

        # -----------------------------
        # Forward Fill
        # -----------------------------

        elif action == "forward_fill":

            try:

                cleaned_df = cleaned_df.with_columns(
                    pl.col(column)
                    .forward_fill()
                    .alias(column)
                )

                cleaning_log.append({
                    "column": column,
                    "action": "forward_fill"
                })

            except Exception:

                pass

    return cleaned_df, cleaning_log