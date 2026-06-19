import re

EMAIL_PATTERN = r'^[\w.-]+@[\w.-]+.\w+$'
URL_PATTERN = r'^https?://'

def detect_semantic_type(column_name, values):

    
    column_name = column_name.lower().strip()

    sample_values = [
        str(v).strip()
        for v in values[:20]
        if v is not None and str(v).strip() != ""
    ]

    # -------------------------
    # ID Detection
    # -------------------------

    if any(
        keyword in column_name
        for keyword in [
            "id",
            "_id",
            "course id",
            "student id",
            "customer id"
        ]
    ):
        return {
            "semantic_type": "ID",
            "confidence": 0.95
        }

    # -------------------------
    # EMAIL Detection
    # -------------------------

    email_count = sum(
        1
        for value in sample_values
        if re.match(EMAIL_PATTERN, value)
    )

    if email_count >= 5:
        return {
            "semantic_type": "EMAIL",
            "confidence": 0.98
        }

    # -------------------------
    # URL Detection
    # -------------------------

    url_count = sum(
        1
        for value in sample_values
        if re.match(URL_PATTERN, value)
    )

    if (
        "url" in column_name
        or "link" in column_name
        or url_count >= 5
    ):
        return {
            "semantic_type": "URL",
            "confidence": 0.98
        }

    # -------------------------
    # PERSON Detection
    # -------------------------

    if any(
        keyword in column_name
        for keyword in [
            "created by",
            "author",
            "creator",
            "instructor",
            "teacher",
            "trainer"
        ]
    ):
        return {
            "semantic_type": "PERSON",
            "confidence": 0.95
        }

    # -------------------------
    # DATE Detection
    # -------------------------

    if any(
        keyword in column_name
        for keyword in [
            "date",
            "dob",
            "timestamp",
            "updated at",
            "created at"
        ]
    ):
        return {
            "semantic_type": "DATE",
            "confidence": 0.90
        }

    # -------------------------
    # PHONE Detection
    # -------------------------

    if any(
        keyword in column_name
        for keyword in [
            "phone",
            "mobile",
            "contact"
        ]
    ):
        return {
            "semantic_type": "PHONE",
            "confidence": 0.90
        }

    # -------------------------
    # PRICE Detection
    # -------------------------

    if any(
        keyword in column_name
        for keyword in [
            "price",
            "cost",
            "fee",
            "amount"
        ]
    ):
        return {
            "semantic_type": "PRICE",
            "confidence": 0.95
        }

    # -------------------------
    # RATING Detection
    # -------------------------

    if "rating" in column_name:
        return {
            "semantic_type": "RATING",
            "confidence": 0.95
        }

    # -------------------------
    # COUNT Detection
    # -------------------------

    if any(
        keyword in column_name
        for keyword in [
            "count",
            "number",
            "viewer",
            "review",
            "ratings"
        ]
    ):
        return {
            "semantic_type": "COUNT",
            "confidence": 0.90
        }

    # -------------------------
    # DURATION Detection
    # -------------------------

    if any(
        keyword in column_name
        for keyword in [
            "duration",
            "weekly study",
            "week",
            "hour",
            "month access"
        ]
    ):
        return {
            "semantic_type": "DURATION",
            "confidence": 0.90
        }

    # -------------------------
    # CATEGORY Detection
    # -------------------------

    if any(
        keyword in column_name
        for keyword in [
            "category",
            "sub-category",
            "type",
            "language",
            "level",
            "school",
            "program"
        ]
    ):
        return {
            "semantic_type": "CATEGORY",
            "confidence": 0.85
        }

    # -------------------------
    # TEXT Detection
    # -------------------------

    if any(
        keyword in column_name
        for keyword in [
            "intro",
            "description",
            "learn",
            "faq",
            "skills",
            "title",
            "include",
            "prerequisite"
        ]
    ):
        return {
            "semantic_type": "TEXT",
            "confidence": 0.85
        }

    # -------------------------
    # Long Text Detection
    # -------------------------

    if sample_values:

        avg_length = (
            sum(len(v) for v in sample_values)
            / len(sample_values)
        )

        if avg_length > 50:

            return {
                "semantic_type": "TEXT",
                "confidence": 0.80
            }

    return {
        "semantic_type": "UNKNOWN",
        "confidence": 0.50
    }

