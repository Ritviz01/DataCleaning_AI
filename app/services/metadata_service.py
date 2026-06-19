def generate_metadata(df):

    return {
        "rows": df.height,
        "columns": df.width,
        "column_names": df.columns
    }