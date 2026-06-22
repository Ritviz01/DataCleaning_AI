import os
import polars as pl


EXPORT_DIR = "exports"

os.makedirs(
    EXPORT_DIR,
    exist_ok=True
)


def export_cleaned_dataset(
    df,
    original_filename
):

    file_name = (
        f"cleaned_{original_filename}"
    )

    export_path = os.path.join(
        EXPORT_DIR,
        file_name
    )

    if original_filename.endswith(".csv"):

        df.write_csv(
            export_path
        )

    elif original_filename.endswith(".xlsx"):

        df.write_excel(
            export_path
        )

    else:

        export_path = export_path + ".csv"

        df.write_csv(
            export_path
        )

    return export_path