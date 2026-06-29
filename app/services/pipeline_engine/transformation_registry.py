import polars as pl
from typing import Callable, Dict, Any, List, Optional
from app.services.type_converter import apply_type_conversions
from app.services.semantic_cleaner import semantic_clean_dataset

class TransformationRegistry:
    def __init__(self):
        self._registry: Dict[str, Callable[[pl.DataFrame, Dict[str, Any]], pl.DataFrame]] = {}
        self._register_default_transformations()

    def register(self, name: str, handler: Callable[[pl.DataFrame, Dict[str, Any]], pl.DataFrame]):
        if name in self._registry:
            raise ValueError(f"Transformation '{name}' is already registered.")
        self._registry[name] = handler

    def get(self, name: str) -> Callable[[pl.DataFrame, Dict[str, Any]], pl.DataFrame]:
        if name not in self._registry:
            raise ValueError(f"Unknown transformation: '{name}'")
        return self._registry[name]

    def list_available(self) -> List[str]:
        return list(self._registry.keys())

    def _register_default_transformations(self):
        # 1. remove_duplicates
        def remove_duplicates(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            subset = params.get("subset")
            if subset and isinstance(subset, str):
                subset = [subset]
            return df.unique(subset=subset, maintain_order=True)

        # 2. fill_missing
        def fill_missing(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            if not column or column not in df.columns:
                return df
            
            method = params.get("method", "value")
            
            if method == "median":
                median_value = df[column].cast(pl.Float64, strict=False).drop_nulls().median()
                if median_value is not None:
                    return df.with_columns(
                        pl.col(column).cast(pl.Float64, strict=False).fill_null(median_value).alias(column)
                    )
            elif method == "mode":
                mode_vals = df[column].drop_nulls().mode()
                if len(mode_vals) > 0:
                    mode_value = mode_vals[0]
                    return df.with_columns(
                        pl.col(column).fill_null(mode_value).alias(column)
                    )
            elif method == "forward_fill":
                return df.with_columns(
                    pl.col(column).forward_fill().alias(column)
                )
            elif method == "value":
                fill_value = params.get("fill_value")
                return df.with_columns(
                    pl.col(column).fill_null(fill_value).alias(column)
                )
            return df

        # 3. drop_column
        def drop_column(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            if column in df.columns:
                return df.drop(column)
            return df

        # 4. rename_column
        def rename_column(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            new_name = params.get("new_name")
            if column in df.columns and new_name:
                return df.rename({column: new_name})
            return df

        # 5. convert_type
        def convert_type(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            target_type = params.get("target_type") or params.get("suggested_type")
            if column in df.columns and target_type:
                # Reuse apply_type_conversions
                return apply_type_conversions(df, [{"column": column, "suggested_type": target_type}])
            return df

        # 6. remove_outliers
        def remove_outliers(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            if not column or column not in df.columns:
                return df
            
            method = params.get("method", "cap") # 'cap' or 'remove'
            try:
                numeric_series = df[column].cast(pl.Float64, strict=False).drop_nulls()
                if len(numeric_series) < 5:
                    return df

                q1 = numeric_series.quantile(0.25)
                q3 = numeric_series.quantile(0.75)
                if q1 is None or q3 is None:
                    return df

                iqr = q3 - q1
                if iqr == 0:
                    return df

                lower_bound = q1 - (1.5 * iqr)
                upper_bound = q3 + (1.5 * iqr)

                if method == "remove":
                    # Filter rows where value is within bounds or is null
                    return df.filter(
                        (pl.col(column).cast(pl.Float64, strict=False) >= lower_bound) &
                        (pl.col(column).cast(pl.Float64, strict=False) <= upper_bound) |
                        pl.col(column).is_null()
                    )
                else:
                    # Default: cap/clip
                    return df.with_columns(
                        pl.col(column).cast(pl.Float64, strict=False).clip(lower_bound, upper_bound).alias(column)
                    )
            except Exception as e:
                print(f"Error in remove_outliers for {column}: {e}")
                return df

        # 7. normalize
        def normalize(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            if not column or column not in df.columns:
                return df
            
            method = params.get("method", "min_max") # 'min_max' or 'z_score'
            try:
                col_cast = pl.col(column).cast(pl.Float64, strict=False)
                if method == "z_score":
                    mean_val = df[column].cast(pl.Float64, strict=False).mean()
                    std_val = df[column].cast(pl.Float64, strict=False).std()
                    if mean_val is not None and std_val is not None and std_val != 0:
                        return df.with_columns(
                            ((col_cast - mean_val) / std_val).alias(column)
                        )
                else:
                    min_val = df[column].cast(pl.Float64, strict=False).min()
                    max_val = df[column].cast(pl.Float64, strict=False).max()
                    if min_val is not None and max_val is not None and max_val != min_val:
                        return df.with_columns(
                            ((col_cast - min_val) / (max_val - min_val)).alias(column)
                        )
            except Exception as e:
                print(f"Error in normalize for {column}: {e}")
            return df

        # 8. encode_categories
        def encode_categories(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            if not column or column not in df.columns:
                return df
            
            method = params.get("method", "label") # 'label' or 'one_hot'
            try:
                unique_vals = df[column].drop_nulls().unique().to_list()
                if not unique_vals:
                    return df

                if method == "one_hot":
                    exprs = [
                        pl.when(pl.col(column) == val).then(1).otherwise(0).alias(f"{column}_{val}")
                        for val in unique_vals
                    ]
                    return df.with_columns(exprs).drop(column)
                else:
                    # Label encoding
                    unique_vals.sort()
                    w = pl.when(pl.col(column) == unique_vals[0]).then(0)
                    for idx, val in enumerate(unique_vals[1:], start=1):
                        w = w.when(pl.col(column) == val).then(idx)
                    return df.with_columns(w.otherwise(None).alias(column))
            except Exception as e:
                print(f"Error in encode_categories for {column}: {e}")
            return df

        # 9. standardize_text
        def standardize_text(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            if column:
                if column not in df.columns:
                    return df
                # Isolate and clean
                temp_df = df.select([column])
                cleaned_temp = semantic_clean_dataset(temp_df)
                return df.with_columns(cleaned_temp[column])
            else:
                return semantic_clean_dataset(df)

        # 10. trim_whitespace
        def trim_whitespace(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            cols_to_trim = [column] if column else [c for c in df.columns if df[c].dtype == pl.Utf8]
            
            for col in cols_to_trim:
                if col in df.columns and df[col].dtype == pl.Utf8:
                    try:
                        df = df.with_columns(pl.col(col).str.strip_chars().alias(col))
                    except AttributeError:
                        df = df.with_columns(pl.col(col).str.strip().alias(col))
            return df

        # 11. lowercase
        def lowercase(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            if column in df.columns and df[column].dtype == pl.Utf8:
                return df.with_columns(pl.col(column).str.to_lowercase().alias(column))
            return df

        # 12. uppercase
        def uppercase(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            if column in df.columns and df[column].dtype == pl.Utf8:
                return df.with_columns(pl.col(column).str.to_uppercase().alias(column))
            return df

        # 13. replace_values
        def replace_values(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            old_val = params.get("old_value")
            new_val = params.get("new_value")
            if column in df.columns:
                return df.with_columns(
                    pl.when(pl.col(column) == old_val).then(new_val).otherwise(pl.col(column)).alias(column)
                )
            return df

        # 14. split_column
        def split_column(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            delimiter = params.get("delimiter", ",")
            new_columns = params.get("new_columns")
            if column in df.columns and new_columns and isinstance(new_columns, list):
                n = len(new_columns) - 1
                try:
                    split_struct = pl.col(column).cast(pl.Utf8).str.split_exact(delimiter, n)
                    exprs = [
                        split_struct.struct.field(f"field_{i}").alias(new_col)
                        for i, new_col in enumerate(new_columns)
                    ]
                    return df.with_columns(exprs).drop(column)
                except Exception as e:
                    print(f"Error in split_column: {e}")
            return df

        # 15. merge_columns
        def merge_columns(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            columns = params.get("columns")
            new_column = params.get("new_column")
            separator = params.get("separator", "")
            if columns and isinstance(columns, list) and new_column:
                existing_cols = [c for c in columns if c in df.columns]
                if existing_cols:
                    expr = pl.concat_str([pl.col(c).cast(pl.Utf8) for c in existing_cols], separator=separator)
                    return df.with_columns(expr.alias(new_column))
            return df

        # 16. feature_engineering
        def feature_engineering(df: pl.DataFrame, params: Dict[str, Any]) -> pl.DataFrame:
            column = params.get("column")
            operation = params.get("operation")
            if not column or column not in df.columns or not operation:
                return df
            
            try:
                col_cast = pl.col(column).cast(pl.Float64, strict=False)
                if operation == "log":
                    return df.with_columns(col_cast.log().alias(f"{column}_log"))
                elif operation == "square":
                    return df.with_columns((col_cast ** 2).alias(f"{column}_sq"))
                elif operation == "sqrt":
                    return df.with_columns(col_cast.sqrt().alias(f"{column}_sqrt"))
                elif operation == "bin":
                    bin_edges = params.get("bin_edges")
                    if not bin_edges:
                        c_min = df[column].cast(pl.Float64, strict=False).min()
                        c_max = df[column].cast(pl.Float64, strict=False).max()
                        if c_min is not None and c_max is not None:
                            step = (c_max - c_min) / 4
                            bin_edges = [c_min + step * i for i in range(5)]
                    
                    if bin_edges and len(bin_edges) > 2:
                        breaks = [float(x) for x in bin_edges[1:-1]]
                        return df.with_columns(
                            pl.col(column).cast(pl.Float64, strict=False).cut(breaks=breaks).alias(f"{column}_binned")
                        )
            except Exception as e:
                print(f"Error in feature_engineering for {column}: {e}")
            return df

        # Register all
        self.register("remove_duplicates", remove_duplicates)
        self.register("fill_missing", fill_missing)
        self.register("drop_column", drop_column)
        self.register("rename_column", rename_column)
        self.register("convert_type", convert_type)
        self.register("remove_outliers", remove_outliers)
        self.register("normalize", normalize)
        self.register("encode_categories", encode_categories)
        self.register("standardize_text", standardize_text)
        self.register("trim_whitespace", trim_whitespace)
        self.register("lowercase", lowercase)
        self.register("uppercase", uppercase)
        self.register("replace_values", replace_values)
        self.register("split_column", split_column)
        self.register("merge_columns", merge_columns)
        self.register("feature_engineering", feature_engineering)

# Global singleton
registry = TransformationRegistry()
