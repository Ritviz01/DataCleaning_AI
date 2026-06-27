import re

EMAIL_PATTERN = r'^[\w.-]+@[\w.-]+.\w+$'
URL_PATTERN = r'^https?://'

def detect_semantic_type(column_name, values, domain="General"):
    column_name = column_name.lower().strip()

    sample_values = [
        str(v).strip()
        for v in values[:20]
        if v is not None and str(v).strip() != ""
    ]

    # 1. Row Index / Record ID Detection
    if (
        column_name == "unnamed: 0"
        or "unnamed" in column_name
        or column_name in ["index", "row", "row_id", "s.no", "sl_no", "serial_number"]
    ):
        return {
            "semantic_type": "RECORD_ID",
            "confidence": 0.99
        }

    # 2. Domain-Specific Inference (Electronics / Laptops)
    if domain.lower() in ("electronics", "electronics_dataset", "laptop", "manufacturing", "ecommerce", "retail"):
        if column_name in ("company", "brand", "manufacturer"):
            return {"semantic_type": "COMPANY", "confidence": 0.99}
        if column_name in ("typename", "type_name", "product_category", "category"):
            return {"semantic_type": "PRODUCT_CATEGORY", "confidence": 0.99}
        if column_name in ("cpu", "processor", "processor_type"):
            return {"semantic_type": "CPU", "confidence": 0.99}
        if column_name in ("ram", "memory_size"):
            return {"semantic_type": "MEMORY", "confidence": 0.99}
        if column_name == "memory" or "storage" in column_name:
            return {"semantic_type": "STORAGE", "confidence": 0.99}
        if column_name in ("gpu", "graphics", "video_card"):
            return {"semantic_type": "GPU", "confidence": 0.99}
        if column_name in ("weight", "mass"):
            return {"semantic_type": "MEASUREMENT", "confidence": 0.99}
        if column_name in ("price", "cost", "msrp"):
            return {"semantic_type": "PRICE", "confidence": 0.99}
        if column_name in ("inches", "screen_size"):
            return {"semantic_type": "MEASUREMENT", "confidence": 0.99}

    # 3. ID Detection
    if any(
        keyword == column_name or f"_{keyword}" in column_name or f" {keyword}" in column_name
        for keyword in ["id", "course_id", "student_id", "customer_id", "employee_id"]
    ):
        return {
            "semantic_type": "ID",
            "confidence": 0.99
        }

    # 4. EMAIL Detection
    email_count = sum(
        1
        for value in sample_values
        if re.match(EMAIL_PATTERN, value)
    )
    if email_count >= 5:
        return {
            "semantic_type": "EMAIL",
            "confidence": 0.99
        }

    # 5. URL Detection
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
            "confidence": 0.99
        }

    # 6. PERSON Detection (Safe matching to avoid substring bugs like Unnamed:0 and TypeName matching as PERSON)
    is_person = (
        column_name == "name"
        or column_name.endswith("_name")
        or column_name.startswith("name_")
        or " name" in column_name
        or "name " in column_name
        or any(
            kw in column_name
            for kw in [
                "person",
                "user",
                "author",
                "creator",
                "instructor",
                "teacher",
                "trainer",
                "student",
                "employee",
                "patient"
            ]
        )
    )
    if is_person:
        # Strictly check for boundary conditions / exceptions
        if not any(exc in column_name for exc in ["unnamed", "type", "file", "domain", "index", "id"]):
            return {
                "semantic_type": "PERSON",
                "confidence": 0.99
            }

    # 7. DATE Detection
    if any(
        keyword in column_name
        for keyword in [
            "date",
            "dob",
            "timestamp",
            "updated_at",
            "created_at"
        ]
    ):
        return {
            "semantic_type": "DATE",
            "confidence": 0.99
        }

    # 8. PHONE Detection
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
            "confidence": 0.99
        }

    # 9. PRICE Detection
    if any(
        keyword in column_name
        for keyword in [
            "price",
            "salary",
            "revenue",
            "amount",
            "payment",
            "cost",
            "fee"
        ]
    ):
        return {
            "semantic_type": "PRICE",
            "confidence": 0.99
        }

    # 10. AGE Detection
    if "age" in column_name:
        return {
            "semantic_type": "AGE",
            "confidence": 0.99
        }

    # 11. MEASUREMENT Detection
    if any(
        keyword in column_name
        for keyword in [
            "weight",
            "measurement",
            "height",
            "length",
            "width",
            "inches"
        ]
    ):
        return {
            "semantic_type": "MEASUREMENT",
            "confidence": 0.99
        }

    # 12. HARDWARE Detection
    if any(
        keyword in column_name
        for keyword in [
            "ram",
            "gpu",
            "cpu",
            "memory"
        ]
    ):
        return {
            "semantic_type": "HARDWARE",
            "confidence": 0.99
        }

    # 13. COMPANY Detection
    if any(
        keyword in column_name
        for keyword in [
            "company",
            "organization"
        ]
    ):
        return {
            "semantic_type": "COMPANY",
            "confidence": 0.99
        }

    # 14. COURSE Detection
    if "course" in column_name:
        return {
            "semantic_type": "COURSE",
            "confidence": 0.99
        }

    # 15. RATING Detection
    if "rating" in column_name:
        return {
            "semantic_type": "RATING",
            "confidence": 0.99
        }

    # 16. COUNT Detection
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
            "confidence": 0.98
        }

    # 17. DURATION Detection
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
            "confidence": 0.98
        }

    # 18. CATEGORY Detection
    if any(
        keyword in column_name
        for keyword in [
            "category",
            "industry",
            "gender",
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
            "confidence": 0.99
        }

    # 19. TEXT Detection
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
            "confidence": 0.95
        }

    # 20. Long Text Detection
    if sample_values:
        avg_length = (
            sum(len(v) for v in sample_values)
            / len(sample_values)
        )
        if avg_length > 50:
            return {
                "semantic_type": "TEXT",
                "confidence": 0.95
            }

    return {
        "semantic_type": "UNKNOWN",
        "confidence": 0.50
    }
