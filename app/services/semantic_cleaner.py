import polars as pl


def semantic_clean_dataset(df):

    cleaned_df = df.clone()

    for column in cleaned_df.columns:

        column_lower = column.lower()

        try:

            # =========================
            # RAM
            # 8GB -> 8
            # =========================

            if "ram" in column_lower:

                cleaned_df = cleaned_df.with_columns(

                    pl.col(column)

                    .cast(pl.Utf8)

                    .str.replace_all(
                        r"[^0-9]",
                        ""
                    )

                    .cast(
                        pl.Int64,
                        strict=False
                    )

                    .alias(column)
                )

            # =========================
            # WEIGHT
            # 2.2kg -> 2.2
            # =========================

            elif "weight" in column_lower:

                cleaned_df = cleaned_df.with_columns(

                    pl.col(column)

                    .cast(pl.Utf8)

                    .str.replace_all(
                        r"[^0-9.]",
                        ""
                    )

                    .cast(
                        pl.Float64,
                        strict=False
                    )

                    .alias(column)
                )

            # =========================
            # PRICE
            # $999 -> 999
            # =========================

            elif (
                "price" in column_lower
                or
                "cost" in column_lower
            ):

                cleaned_df = cleaned_df.with_columns(

                    pl.col(column)

                    .cast(pl.Utf8)

                    .str.replace_all(
                        r"[^0-9.]",
                        ""
                    )

                    .cast(
                        pl.Float64,
                        strict=False
                    )

                    .alias(column)
                )

            # =========================
            # RATING
            # 4.7stars -> 4.7
            # =========================

            elif "rating" in column_lower:

                cleaned_df = cleaned_df.with_columns(

                    pl.col(column)

                    .cast(pl.Utf8)

                    .str.replace_all(
                        r"[^0-9.]",
                        ""
                    )

                    .cast(
                        pl.Float64,
                        strict=False
                    )

                    .alias(column)
                )

            # =========================
            # VIEWERS / REVIEWS
            # =========================

            elif (

                "viewer" in column_lower
                or
                "review" in column_lower
                or
                "rating_count" in column_lower
                or
                "count" in column_lower

            ):

                cleaned_df = cleaned_df.with_columns(

                    pl.col(column)

                    .cast(pl.Utf8)

                    .str.replace_all(
                        r"[^0-9]",
                        ""
                    )

                    .cast(
                        pl.Int64,
                        strict=False
                    )

                    .alias(column)
                )

        except Exception as e:

            print(
                f"Semantic cleaning failed for {column}: {e}"
            )

    return cleaned_df