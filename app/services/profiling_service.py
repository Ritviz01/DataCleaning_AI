def profile_dataset(df):

    profile = []

    total_rows = df.height

    for column in df.columns:

        null_count = df[column].null_count()

        unique_values = df[column].n_unique()

        duplicate_values = total_rows - unique_values

        profile.append({
            "column_name": column,
            "null_count": null_count,
            "null_percentage": round((null_count / total_rows) * 100, 2) if total_rows else 0.0,
            "unique_values": unique_values,
            "duplicate_values": duplicate_values
        })

    return profile
