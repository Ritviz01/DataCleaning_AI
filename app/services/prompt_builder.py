def build_dataset_prompt(
    metadata,
    schema,
    quality,
    issues,
    profile=None,
    recommendations=None,
    type_suggestions=None,
    sample_rows=None,
    business_context=None
):
    # Extract dataset type
    dataset_type = "general_dataset"
    if business_context and "dataset_type" in business_context:
        dataset_type = business_context["dataset_type"]

    # Extract column names and semantic types
    column_names = metadata.get("column_names", []) if metadata else []
    if not column_names and schema:
        column_names = [col.get("column_name") for col in schema]
        
    semantic_types = []
    if schema:
        semantic_types = [f"{col.get('column_name')} ({col.get('semantic_type')})" for col in schema]

    prompt = f"""You are a Senior Data Analyst and Data Quality Consultant.

Dataset Type:
{dataset_type}

IMPORTANT RULES:

If dataset_type = reference_dataset:
Only generate:
1. Dataset Purpose
2. Data Quality Summary
3. Available Categories
4. Dashboard Suggestions

DO NOT generate:
- KPI Suggestions
- Risks
- Business Strategy
- Market Share
- Revenue Analysis
- Growth Analysis
- Recommendations

For the KPI Suggestions section when dataset_type = reference_dataset, return exactly:
"No KPI generation possible because the dataset contains only reference categories."

---

DYNAMIC BLOCKS:

1. KPI Suggestions:
Generate KPI suggestions ONLY if numeric columns exist in the dataset.
If no numeric columns exist, return exactly:
"No KPI generation possible."

2. Recommendations:
Generate recommendations ONLY if actual data issues exist (the issues list is not empty).
If the issues list is empty, return exactly:
"No recommendations required."

---

DATASET DETAILS:
- Metadata: {metadata}
- Available Columns: {column_names}
- Detected Semantic Types: {semantic_types}
- Profile: {profile}
- Issues: {issues}
- Recommendations: {recommendations}
- Quality Score: {quality}
- Type Suggestions: {type_suggestions}
- Dataset Sample (First 10 rows): {sample_rows}

Instructions:
1. Conduct a deep analysis of the dataset quality and profile.
2. Under no circumstances should you repeat or dump the raw metadata (like row count, column lists, or basic structure) back in the output. Instead, analyze it qualitatively.
3. NEVER assume the existence of columns that are not present in the dataset.
4. NEVER infer or mention metrics such as revenue, profit, sales, market share, growth rate, employee count, customer counts, or financial KPIs unless corresponding columns exist in the dataset.
5. If the dataset does not contain enough information to generate advanced business insights, explicitly state: "This dataset does not contain enough information to generate advanced business insights."
6. You must structure your response using exactly the following section headings:
   - Executive Summary
   - Dataset Purpose
   - Data Quality Analysis
   - Business Insights / Available Categories
   - Risks
   - Recommendations
   - Dashboard Suggestions
   - KPI Suggestions
"""
    return prompt


def build_analyst_prompt(question: str, dataset_metadata: dict, schema: list[dict]) -> str:
    """Build a structured prompt to convert a user question into Polars code."""
    column_names = dataset_metadata.get("column_names", []) if dataset_metadata else []
    if not column_names and schema:
        column_names = [col.get("column_name") for col in schema]

    semantic_types = []
    if schema:
        semantic_types = [
            f"{col.get('column_name')} (semantic type: {col.get('semantic_type') or 'N/A'}, data type: {col.get('data_type') or 'N/A'})"
            for col in schema
        ]

    prompt = f"""You are an expert AI Data Analyst. Your task is to translate a natural language question about a dataset into a safe, valid Polars dataframe operation.

DATASET INFORMATION:
- Metadata: {dataset_metadata}
- Available Columns: {column_names}
- Column Details: {semantic_types}

USER QUESTION:
"{question}"

CRITICAL RULES:
1. ONLY use the columns listed above. NEVER invent or assume any columns.
2. Generate ONLY valid Polars logic. The dataframe is named `df`.
3. Never use python's `eval()` or write code outside of Polars operations.
4. Output must be a single expression or operation on the `df` object. Examples:
   - "Top 5 most expensive laptops":
     df.sort("Price", descending=True).head(5)
   - "Average price by company":
     df.group_by("Company").agg(pl.col("Price").mean())
   - "Show all students older than 25":
     df.filter(pl.col("Age") > 25)
5. Do NOT include markdown blocks (like ```json ... ```) in your response. Output a single, valid JSON object only.
6. The JSON response MUST match this structure:
{{
  "explanation": "A concise natural language explanation of how you are querying the dataset to answer the user's question.",
  "polars_code": "df.sort(\\"Price\\", descending=True).head(5)",
  "required_columns": ["Price"]
}}
"""
    return prompt