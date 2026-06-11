import re

EMAIL_PATTERN = r'^[\w\.-]+@[\w\.-]+\.\w+$'


def detect_semantic_type(column_name, values):

    column_name = column_name.lower()

    # ID detection
    if "id" in column_name:
        return {
            "semantic_type": "ID",
            "confidence": 0.95
        }

    # Email detection
    email_count = 0

    for value in values[:20]:

        if value is None:
            continue

        if re.match(EMAIL_PATTERN, str(value)):
            email_count += 1

    if email_count >= 5:
        return {
            "semantic_type": "EMAIL",
            "confidence": 0.98
        }

    # Date detection
    if "date" in column_name:
        return {
            "semantic_type": "DATE",
            "confidence": 0.90
        }

    # Phone detection
    if "phone" in column_name or "mobile" in column_name:
        return {
            "semantic_type": "PHONE",
            "confidence": 0.90
        }

    return {
        "semantic_type": "UNKNOWN",
        "confidence": 0.50
    }