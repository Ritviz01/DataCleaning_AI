def build_dataset_prompt(
    metadata,
    schema,
    quality,
    issues
):

    prompt = f"""

You are a Senior Data Analyst.

Analyze the dataset.

DATASET INFO:
Rows: {metadata['rows']}
Columns: {metadata['columns']}

QUALITY:
Score: {quality['quality_score']}
Grade: {quality['grade']}

SCHEMA:
{schema}

ISSUES:
{issues}

Generate:

1. Executive Summary
2. Data Quality Analysis
3. Major Problems
4. Business Insights
5. Dashboard Recommendations
6. Data Cleaning Recommendations

Return concise professional output.

"""

    return prompt