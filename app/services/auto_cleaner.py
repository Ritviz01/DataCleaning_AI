import polars as pl
from app.services.type_converter import apply_type_conversions

def auto_clean_dataset(
    df,
    recommendations,
    type_suggestions=None
):
    cleaned_df = df.clone()
    cleaning_log = []

    # ==========================================
    # Backward compatible Type Conversion (from suggestions parameter)
    # ==========================================
    if type_suggestions:
        try:
            cleaned_df = apply_type_conversions(
                cleaned_df,
                type_suggestions
            )
            cleaning_log.append({
                "action": "type_conversion",
                "columns_processed": len(type_suggestions),
                "details": f"Processed {len(type_suggestions)} column type conversions from suggestions."
            })
        except Exception as e:
            print(f"Type Conversion Error: {e}")

    # ==========================================
    # Apply Recommendations
    # ==========================================
    for recommendation in recommendations:
        column = recommendation.get("column")
        action = recommendation.get("recommended_action")

        # ======================================
        # REMOVE DUPLICATES
        # ======================================
        if action == "remove_duplicates":
            try:
                before = cleaned_df.height
                cleaned_df = cleaned_df.unique()
                after = cleaned_df.height
                cleaning_log.append({
                    "action": "remove_duplicates",
                    "rows_removed": before - after,
                    "details": f"Removed {before - after} duplicate rows."
                })
            except Exception as e:
                print(f"Error in remove_duplicates: {e}")
            continue

        # ======================================
        # Column Exists?
        # ======================================
        if not column or column not in cleaned_df.columns:
            continue

        # ======================================
        # DROP COLUMN
        # ======================================
        if action == "drop_column":
            try:
                cleaned_df = cleaned_df.drop(column)
                cleaning_log.append({
                    "column": column,
                    "action": "drop_column",
                    "details": f"Dropped column '{column}'."
                })
            except Exception as e:
                print(f"Error dropping column {column}: {e}")

        # ======================================
        # MEDIAN IMPUTATION
        # ======================================
        elif action == "median_imputation":
            try:
                median_value = (
                    cleaned_df[column]
                    .cast(pl.Float64, strict=False)
                    .median()
                )
                cleaned_df = cleaned_df.with_columns(
                    pl.col(column)
                    .cast(pl.Float64, strict=False)
                    .fill_null(median_value)
                    .alias(column)
                )
                cleaning_log.append({
                    "column": column,
                    "action": "median_imputation",
                    "value_used": median_value,
                    "details": f"Imputed missing values in '{column}' using median: {median_value}."
                })
            except Exception as e:
                print(f"Error in median_imputation for {column}: {e}")

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
                    mode_value = mode_value[0]
                    cleaned_df = cleaned_df.with_columns(
                        pl.col(column)
                        .fill_null(mode_value)
                        .alias(column)
                    )
                    cleaning_log.append({
                        "column": column,
                        "action": "mode_imputation",
                        "value_used": str(mode_value),
                        "details": f"Imputed missing values in '{column}' using mode: {mode_value}."
                    })
            except Exception as e:
                print(f"Error in mode_imputation for {column}: {e}")

        # ======================================
        # FORWARD FILL
        # ======================================
        elif action == "forward_fill":
            try:
                cleaned_df = cleaned_df.with_columns(
                    pl.col(column)
                    .forward_fill()
                    .alias(column)
                )
                cleaning_log.append({
                    "column": column,
                    "action": "forward_fill",
                    "details": f"Forward filled missing values in '{column}'."
                })
            except Exception as e:
                print(f"Error in forward_fill for {column}: {e}")

        # ======================================
        # OUTLIER CAPPING
        # ======================================
        elif action == "cap_outliers":
            try:
                numeric_series = (
                    cleaned_df[column]
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

                cleaned_df = cleaned_df.with_columns(
                    pl.col(column)
                    .cast(pl.Float64, strict=False)
                    .clip(lower_bound, upper_bound)
                    .alias(column)
                )

                cleaning_log.append({
                    "column": column,
                    "action": "cap_outliers",
                    "lower_bound": round(lower_bound, 2),
                    "upper_bound": round(upper_bound, 2),
                    "details": f"Capped outliers in '{column}' within bounds [{round(lower_bound, 2)}, {round(upper_bound, 2)}]."
                })
            except Exception as e:
                print(f"Error in cap_outliers for {column}: {e}")

        # ======================================
        # TYPE CONVERSION (First-class Action)
        # ======================================
        elif action == "type_conversion":
            try:
                target_type = recommendation.get("suggested_type") or recommendation.get("target_type")
                if not target_type and type_suggestions:
                    target_type = next((s["suggested_type"] for s in type_suggestions if s["column"] == column), None)
                
                if target_type:
                    cleaned_df = apply_type_conversions(
                        cleaned_df,
                        [{"column": column, "suggested_type": target_type}]
                    )
                    cleaning_log.append({
                        "column": column,
                        "action": "type_conversion",
                        "target_type": target_type,
                        "details": f"Converted column '{column}' to type '{target_type}'."
                    })
            except Exception as e:
                print(f"Error in type_conversion for {column}: {e}")

    return cleaned_df, cleaning_log
