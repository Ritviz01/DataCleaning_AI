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


def build_analyst_prompt(
    question: str,
    dataset_metadata: dict,
    schema: list[dict],
    dataset_type: str,
    history: list[dict]
) -> str:
    """Build a structured prompt to convert a user question into a JSON-based Polars query plan."""
    column_names = dataset_metadata.get("column_names", []) if dataset_metadata else []
    if not column_names and schema:
        column_names = [col.get("column_name") for col in schema]

    semantic_types = []
    if schema:
        semantic_types = [
            f"{col.get('column_name')} (semantic: {col.get('semantic_type') or 'N/A'}, type: {col.get('data_type') or 'N/A'})"
            for col in schema
        ]

    # Format history for prompt
    history_str = "No prior conversation history."
    if history:
        history_str = ""
        for i, turn in enumerate(history, 1):
            history_str += f"[Turn {i}]\n"
            history_str += f"User Question: {turn['question']}\n"
            history_str += f"Assistant Plan: {turn['query_plan']}\n"
            history_str += f"Assistant Insight: {turn.get('insight', 'N/A')}\n\n"

    prompt = f"""You are an expert AI Data Analyst. Your task is to translate a user's natural language question into a structured JSON query plan representing dataframe operations.

DATASET DETAILS:
- Dataset Type: {dataset_type}
- Metadata: {dataset_metadata}
- Available Columns: {column_names}
- Column Details: {semantic_types}

CONVERSATION HISTORY:
{history_str}

CURRENT USER QUESTION:
"{question}"

CRITICAL RULES:
1. ONLY use columns listed in the available columns. NEVER invent, assume, or hallucinate columns or tables.
2. If the current question builds upon or refers to prior turns (e.g. "Only HP" after "Top 10 expensive laptops"), merge/augment the steps from the previous turn's query plan appropriately to preserve context (e.g., adding a filter step to the sorting/limiting logic).
3. Do NOT output raw python code or free-form text. Output valid raw JSON only.
4. Supported operations and properties:
   - "filter": filters rows.
     Properties: "column" (str), "operator" (str: "equals", "not_equals", "greater_than", "less_than", "greater_than_or_equal", "less_than_or_equal", "contains", "in"), "value" (Any).
   - "groupby": groups and aggregates.
     Properties: "group" (list of str or str), "target" (str), "aggregation" (str: "mean", "median", "sum", "min", "max", "count").
   - "sort": sorts dataframe.
     Properties: "column" (str), "order" (str: "ascending" or "descending"), "limit" (optional int).
   - "head" or "tail": limits rows.
     Properties: "limit" (int).
   - "unique": returns unique values.
     Properties: "column" (str).
   - "value_counts": counts frequencies.
     Properties: "column" (str).
   - "mean" / "median" / "max" / "min" / "sum" / "count": computes statistics.
     Properties: "column" (str).

Your JSON output MUST match this exact schema:
{{
  "steps": [
    {{
      "operation": "filter",
      "column": "Company",
      "operator": "equals",
      "value": "HP"
    }}
  ]
}}
"""
    return prompt