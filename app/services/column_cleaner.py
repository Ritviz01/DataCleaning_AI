# Clean column names
def clean_column_names(df):

    # Har column name se extra spaces remove karo
    df.columns = [
        col.strip()
        for col in df.columns
    ]

    # Cleaned dataframe return karo
    return df