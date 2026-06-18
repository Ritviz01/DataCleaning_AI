import polars as pl


def apply_type_conversions(
    df,
    type_suggestions
):

    converted_df = df.clone()

    for suggestion in type_suggestions:

        column = suggestion.get(
            "column"
        )

        target_type = suggestion.get(
            "suggested_type"
        )

        if column not in converted_df.columns:
            continue

        try:

            # ==========================
            # INTEGER
            # ==========================

            if target_type == "Integer":

                converted_df = (
                    converted_df
                    .with_columns(

                        pl.col(column)

                        .cast(pl.Utf8)

                        .str.replace_all(
                            r"[^0-9-]",
                            ""
                        )

                        .cast(
                            pl.Int64,
                            strict=False
                        )

                        .alias(column)
                    )
                )

            # ==========================
            # FLOAT
            # ==========================

            elif target_type == "Float":

                converted_df = (
                    converted_df
                    .with_columns(

                        pl.col(column)

                        .cast(pl.Utf8)

                        .str.replace_all(
                            r"[^0-9.-]",
                            ""
                        )

                        .cast(
                            pl.Float64,
                            strict=False
                        )

                        .alias(column)
                    )
                )

            # ==========================
            # DATE
            # ==========================

            elif target_type == "Date":

                converted_df = (
                    converted_df
                    .with_columns(

                        pl.col(column)

                        .str.strptime(
                            pl.Date,
                            strict=False
                        )

                        .alias(column)
                    )
                )

            # ==========================
            # BOOLEAN
            # ==========================

            elif target_type == "Boolean":

                converted_df = (
                    converted_df
                    .with_columns(

                        pl.when(

                            pl.col(column)
                            .cast(pl.Utf8)
                            .str.to_lowercase()

                            .is_in(
                                [
                                    "true",
                                    "yes",
                                    "1"
                                ]
                            )

                        )

                        .then(True)

                        .otherwise(False)

                        .alias(column)
                    )
                )

        except Exception as e:

            print(
                f"Type conversion failed for {column}: {e}"
            )

    return converted_df