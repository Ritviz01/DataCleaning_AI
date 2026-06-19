# File encoding detect karne ke liye
from app.services.encoding_detector import detect_encoding

import polars as pl
import csv


def read_dataset(file_path: str, file_type: str):

    # -----------------------------
    # CSV FILES
    # -----------------------------
    if file_type == "csv":

        encoding = detect_encoding(file_path)

        print(
            f"Detected Encoding: {encoding}"
        )

        with open(
            file_path,
            "r",
            encoding=encoding,
            errors="ignore"
        ) as f:

            lines = f.readlines()

        # Header line
        header = lines[0].strip()

        # ---------------------------------
        # Mixed CSV Detection
        # Header comma separated
        # Data pipe separated
        # ---------------------------------

        if "," in header:

            pipe_rows = 0

            for line in lines[1:20]:

                if "|" in line:
                    pipe_rows += 1

            if pipe_rows > 5:

                print(
                    "Detected mixed CSV format "
                    "(comma header + pipe rows)"
                )

                columns = [

                    col.strip()

                    for col in header.split(",")

                ]

                cleaned_rows = []

                for line in lines[1:]:

                    if not line.strip():
                        continue

                    values = []

                    for value in line.split("|"):

                        cleaned_value = (
                            value
                            .strip()
                            .rstrip(",")
                        )

                        values.append(
                            cleaned_value
                        )

                    if len(values) == len(columns):

                        cleaned_rows.append(
                            values
                        )

                return pl.DataFrame(
                    cleaned_rows,
                    schema=columns,
                    orient="row"
                )

        # ---------------------------------
        # Normal CSV Detection
        # ---------------------------------

        sample = "".join(
            lines[:20]
        )

        try:

            delimiter = (
                csv.Sniffer()
                .sniff(
                    sample,
                    delimiters=",;|\t"
                )
                .delimiter
            )

        except Exception:

            delimiter = ","

        print(
            f"Detected Delimiter: {delimiter}"
        )

        return pl.read_csv(

            file_path,

            separator=delimiter,

            encoding=encoding,

            ignore_errors=True,

            try_parse_dates=True,

            null_values=[
                "",
                "NA",
                "NULL",
                "null"
            ]

        )

    # -----------------------------
    # EXCEL
    # -----------------------------

    elif file_type == "excel":

        return pl.read_excel(
            file_path
        )

    # -----------------------------
    # JSON
    # -----------------------------

    elif file_type == "json":

        return pl.read_json(
            file_path
        )

    # -----------------------------
    # PARQUET
    # -----------------------------

    elif file_type == "parquet":

        return pl.read_parquet(
            file_path
        )

    else:

        raise ValueError(

            f"Unsupported file type: "
            f"{file_type}"

        )