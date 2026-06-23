import polars as pl
from app.services.semantic_detector import detect_semantic_type
from app.services.type_inference_engine import infer_better_types
from app.services.business_insight_engine import generate_business_context, classify_dataset
from app.services.dashboard_recommender import generate_dashboard_recommendations
from app.services.outlier_detector import detect_outliers
from app.services.auto_cleaner import auto_clean_dataset
from app.services.dataset_insight_engine import generate_dataset_insights
from app.services.openai_service import validate_and_sanitize_response
from app.services.prompt_builder import build_dataset_prompt

def test_semantic_mappings():
    res = detect_semantic_type("salary", [])
    assert res["semantic_type"] == "PRICE"
    assert res["confidence"] == 0.99
    
    res = detect_semantic_type("industry", [])
    assert res["semantic_type"] == "CATEGORY"
    assert res["confidence"] == 0.99

def test_type_inference_numeric_strings():
    df = pl.DataFrame({
        "age_col": ["25", "30", "22", "35", "40"],
        "price_col": ["49999.99", "120.50", "300.00", "45.00", "99.99"],
        "salary_col": ["$5000", "$6000", "$4500", "$7000", "$5500"],
        "ram_col": ["8GB", "16GB", "8GB", "4GB", "32GB"],
        "weight_col": ["2.5kg", "1.8kg", "2.0kg", "3.1kg", "1.5kg"],
        "non_numeric": ["abc", "def", "ghi", "jkl", "mno"]
    })
    
    schema = [
        {"column_name": "age_col", "semantic_type": "AGE"},
        {"column_name": "price_col", "semantic_type": "PRICE"},
        {"column_name": "salary_col", "semantic_type": "PRICE"},
        {"column_name": "ram_col", "semantic_type": "HARDWARE"},
        {"column_name": "weight_col", "semantic_type": "MEASUREMENT"},
        {"column_name": "non_numeric", "semantic_type": "TEXT"}
    ]
    
    suggestions = infer_better_types(df, schema)
    suggestion_map = {s["column"]: s["suggested_type"] for s in suggestions}
    
    assert suggestion_map["age_col"] == "Integer"
    assert suggestion_map["price_col"] == "Float"
    assert suggestion_map["salary_col"] == "Float"
    assert suggestion_map["ram_col"] == "Integer-like"
    assert suggestion_map["weight_col"] == "Float-like"
    assert "non_numeric" not in suggestion_map

def test_business_insights():
    df_student = pl.DataFrame({
        "student_id": ["S1", "S2", "S3"],
        "course": ["Math", "Science", "Math"],
        "grade": ["A", "B", "A"]
    })
    schema_student = [
        {"column_name": "student_id", "semantic_type": "ID"},
        {"column_name": "course", "semantic_type": "COURSE"},
        {"column_name": "grade", "semantic_type": "CATEGORY"}
    ]
    
    ctx = generate_business_context(df_student, schema_student)
    assert ctx["dataset_type"] == "education_dataset"
    assert "student" in ctx["business_context"]
    assert len(ctx["recommended_kpis"]) > 0

def test_outlier_skips():
    df = pl.DataFrame({
        "id_col": [1, 2, 3, 4, 5, 100],  # Outlier 100
        "price_col": [10.0, 12.0, 11.0, 13.0, 12.0, 1000.0]  # Outlier 1000.0
    })
    
    outliers = detect_outliers(df)
    cols_with_outliers = [o["column"] for o in outliers]
    
    assert "price_col" in cols_with_outliers
    assert "id_col" not in cols_with_outliers

def test_auto_cleaner_actions():
    df = pl.DataFrame({
        "ram": ["8GB", "16GB", "8GB"],
        "price": [100.0, 150.0, 100.0]
    })
    
    recommendations = [
        {"column": "ALL", "recommended_action": "remove_duplicates"},
        {"column": "ram", "recommended_action": "type_conversion", "suggested_type": "Integer-like"}
    ]
    
    cleaned, log = auto_clean_dataset(df, recommendations)
    
    assert cleaned.height == 2
    assert cleaned["ram"].dtype == pl.Int64
    assert sorted(cleaned["ram"].to_list()) == [8, 16]
    
    actions = [item["action"] for item in log]
    assert "remove_duplicates" in actions
    assert "type_conversion" in actions

def test_industry_only_dataset():
    df = pl.DataFrame({
        "Industry": ["Healthcare", "Finance", "Technology", "Healthcare"]
    })
    schema = [{"column_name": "Industry", "semantic_type": "CATEGORY"}]
    
    # 1. Business insight classification
    biz = generate_business_context(df, schema)
    assert biz["dataset_type"] == "reference_dataset"
    assert biz["business_context"] == "Reference dataset containing lookup classifications."
    assert "Industry Count" in biz["recommended_kpis"]
    assert "revenue" not in "".join(biz["recommended_kpis"]).lower()
    
    # 2. Dashboard recommender restrictions
    recs = generate_dashboard_recommendations(biz["dataset_type"], df, schema)
    chart_names = [r["chart_name"] for r in recs]
    assert "Industry Distribution" in chart_names
    assert "Industry Frequency" in chart_names
    assert "Category Breakdown" in chart_names
    # Disallowed:
    assert "Revenue Trend" not in chart_names
    assert "Sales Analysis" not in chart_names

def test_small_dataset_insights():
    df = pl.DataFrame({
        "Industry": ["Healthcare", "Finance"] # Only 2 rows
    })
    schema = [{"column_name": "Industry", "semantic_type": "CATEGORY"}]
    metadata = {"rows": 2, "columns": 1}
    quality = {"quality_score": 100.0, "grade": "A"}
    issues = []
    
    insights = generate_dataset_insights(df, schema, metadata, quality, issues)
    assert insights["business_insights"] == [
        "This dataset does not contain enough information to generate advanced business insights."
    ]
    assert insights["recommended_kpis"] == []

def test_post_processing_validation():
    # Columns do not contain revenue, profit, or growth rate
    metadata = {"column_names": ["Industry", "Category"]}
    schema = [
        {"column_name": "Industry", "semantic_type": "CATEGORY"},
        {"column_name": "Category", "semantic_type": "CATEGORY"}
    ]
    
    hallucinated_text = (
        "Executive Summary\n"
        "This is an industry dataset.\n"
        "Revenue increased by 10% this year.\n"
        "Risks\n"
        "Profit might decline next quarter."
    )
    
    sanitized = validate_and_sanitize_response(hallucinated_text, schema, metadata)
    assert "Revenue" not in sanitized
    assert "Profit" not in sanitized
    assert "industry dataset" in sanitized.lower()

def test_prompt_builder_fallbacks():
    metadata = {"column_names": ["Industry"]}
    schema = [{"column_name": "Industry", "semantic_type": "CATEGORY"}]
    quality = {"quality_score": 100.0}
    issues = []
    business_context = {"dataset_type": "reference_dataset"}
    
    prompt = build_dataset_prompt(
        metadata, schema, quality, issues, business_context=business_context
    )
    assert "Dataset Type:\nreference_dataset" in prompt
    assert "No KPI generation possible because the dataset contains only reference categories." in prompt
    assert "No recommendations required." in prompt
