from app.services.dataframe_agent import generate_operations

def generate_query_plan(question: str, dataset_metadata: dict, schema: list[dict]) -> dict:
    """Accepts a user question, uses the dataframe agent to generate the query plan."""
    return generate_operations(question, dataset_metadata, schema)
