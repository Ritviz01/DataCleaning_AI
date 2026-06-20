def get_grade(score):

    if score >= 90:
        return "A"

    elif score >= 80:
        return "B"

    elif score >= 70:
        return "C"

    elif score >= 60:
        return "D"

    return "F"


def calculate_quality_score(profile, issues):

    # ==========================================
    # COMPLETENESS SCORE
    # ==========================================

    total_cells = 0
    missing_cells = 0

    for col in profile:

        total_values = (
            col["unique_values"]
            + col["duplicate_values"]
        )

        total_cells += total_values

        missing_cells += col["null_count"]

    completeness_score = ((total_cells - missing_cells) / total_cells) * 100 if total_cells else 100.0

    # ==========================================
    # UNIQUENESS SCORE
    # ==========================================

    uniqueness_score = 100

    duplicate_id_found = False

    for issue in issues:

        if issue["issue_type"] == "duplicate_ids":

            duplicate_id_found = True

            duplicate_count = issue.get(
                "count",
                0
            )

            penalty = min(
                duplicate_count * 0.002,
                20
            )

            uniqueness_score -= penalty

    uniqueness_score = max(
        0,
        uniqueness_score
    )

    # ==========================================
    # CONSISTENCY SCORE
    # ==========================================

    consistency_score = 100

    constant_columns = 0

    for issue in issues:

        if issue["issue_type"] == "constant_column":

            constant_columns += 1

    consistency_score -= min(
        constant_columns * 2,
        20
    )

    consistency_score = max(
        0,
        consistency_score
    )

    # ==========================================
    # VALIDITY SCORE
    # ==========================================

    validity_score = 100

    processed = set()

    for issue in issues:

        key = (
            issue["column"],
            issue["issue_type"]
        )

        if key in processed:
            continue

        processed.add(key)

        if issue["issue_type"] == "outliers":

            outlier_count = issue.get(
                "count",
                0
            )

            penalty = min(
                outlier_count * 0.001,
                15
            )

            validity_score -= penalty

    validity_score = max(
        0,
        validity_score
    )

    # ==========================================
    # FINAL WEIGHTED SCORE
    # ==========================================

    final_score = (

        completeness_score * 0.40 +

        uniqueness_score * 0.25 +

        consistency_score * 0.15 +

        validity_score * 0.20

    )

    final_score = round(
        final_score,
        2
    )

    return {

        "quality_score": final_score,

        "grade": get_grade(
            final_score
        ),

        "sub_scores": {

            "completeness": round(
                completeness_score,
                2
            ),

            "uniqueness": round(
                uniqueness_score,
                2
            ),

            "consistency": round(
                consistency_score,
                2
            ),

            "validity": round(
                validity_score,
                2
            )

        }

    }
