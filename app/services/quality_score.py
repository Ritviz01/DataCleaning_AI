# Convert numeric score into grade
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


# Calculate quality score from detected issues
def calculate_quality_score(issues):

    # Start with perfect score
    score = 100

    # Check every detected issue
    for issue in issues:

        # Missing value penalty
        if issue["issue_type"] == "missing_values":

            score -= issue["percentage"] * 0.5

        # Duplicate rows penalty
        elif issue["issue_type"] == "duplicate_rows":

            score -= 10

    # Prevent negative score
    score = max(0, round(score, 2))

    return {
        "quality_score": score,
        "grade": get_grade(score)
    }