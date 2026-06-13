import re
from datetime import datetime


# -----------------------------
# Email Validator
# -----------------------------
def is_valid_email(email):

    # Null value hai
    if email is None:
        return False

    # Convert to string
    email = str(email).strip()

    # Standard email regex
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return bool(
        re.match(pattern, email)
    )


# -----------------------------
# Date Validator
# -----------------------------
def is_valid_date(date_value):

    # Null value
    if date_value is None:
        return False

    # Convert to string
    date_value = str(date_value).strip()

    if date_value.upper() in [
        "",
        "NA",
        "N/A",
        "NULL",
        "NONE"
    ]:
        return True

    # Supported date formats
    formats = [

        # Standard formats
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m-%d-%Y",

        "%Y/%m/%d",
        "%d/%m/%Y",
        "%m/%d/%Y",

        # Datetime formats
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",

        # Month name formats
        "%d-%b-%Y",
        "%d-%B-%Y",

        "%b %d %Y",
        "%B %d %Y",

        "%d %b %Y",
        "%d %B %Y"
    ]

    # Try every format
    for fmt in formats:

        try:

            datetime.strptime(
                date_value,
                fmt
            )

            return True

        except ValueError:

            pass

    return False