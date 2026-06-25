import os
from openai import OpenAI

def generate_query_insights(question: str, query_result: list, dataset_metadata: dict, schema: list[dict]) -> str:
    """Uses LLM to generate business insights based on actual query results."""
    if not query_result:
        return "No data returned by the query, so no insights can be generated."

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

    prompt = f"""You are a professional Business Intelligence Analyst. Your task is to look at a user's question, the actual query results, and the schema/metadata to generate simple, high-value business insights.

USER QUESTION:
"{question}"

ACTUAL QUERY RESULTS (first 50 rows):
{query_result[:50]}

DATASET METADATA:
{dataset_metadata}

DATASET SCHEMA:
{schema}

CRITICAL RULES:
1. Under no circumstances should you invent or hallucinate any numbers, names, or values. Only talk about values explicitly present in the query results.
2. Keep the insight brief, professional, and actionable (maximum of 2-3 sentences or a short paragraph).
3. Do not repeat raw data points as-is unless framing them in a business context.
4. If no interesting insight or relationship can be drawn, simply return: "No significant insights found in this subset of data."
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a professional Business Intelligence Analyst who provides direct, fact-based insights without hallucination."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    insight = response.choices[0].message.content.strip()
    return insight
