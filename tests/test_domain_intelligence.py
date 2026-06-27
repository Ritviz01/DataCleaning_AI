import polars as pl
from app.services.dataset_classifier import classify_dataset_locally
from app.services.schema_engine import infer_schema
from app.services.business_insight_engine import generate_business_context
from app.services.openai_service import sanitize_text

def test_laptop_semantic_types():
    # 1. Laptop columns mapping
    df = pl.DataFrame({
        "Company": ["Dell", "Apple", "HP"],
        "Cpu": ["Intel Core i7", "Apple M1", "Intel Core i5"],
        "Ram": ["8GB", "16GB", "8GB"],
        "Memory": ["256GB SSD", "512GB SSD", "1TB HDD"],
        "Gpu": ["Intel Iris", "Apple GPU", "NVIDIA RTX"],
        "Price": [1200.0, 2000.0, 800.0],
        "TypeName": ["Ultrabook", "Notebook", "Notebook"],
        "Unnamed: 0": [1, 2, 3]
    })
    
    res = classify_dataset_locally(df.columns)
    assert res["dataset_type"] == "Electronics"
    
    schema = infer_schema(df, domain="Electronics")
    sem_types = {col["column_name"]: col["semantic_type"] for col in schema}
    
    assert sem_types["Company"] == "COMPANY"
    assert sem_types["Cpu"] == "CPU"
    assert sem_types["Ram"] == "MEMORY"
    assert sem_types["Memory"] == "STORAGE"
    assert sem_types["Gpu"] == "GPU"
    assert sem_types["Price"] == "PRICE"
    assert sem_types["TypeName"] == "PRODUCT_CATEGORY"
    assert sem_types["Unnamed: 0"] == "RECORD_ID"

def test_hallucination_sanitizer():
    # 2. Sanitizer deletes sentences with "Revenue" or "Profit" if indicating columns are absent
    schema = [{"column_name": "student_id", "semantic_type": "ID"}]
    metadata = {"column_names": ["student_id"]}
    
    text = "We track student logins. The revenue of the school is $10000. We also track course completion."
    sanitized = sanitize_text(text, schema, metadata)
    assert "revenue" not in sanitized.lower()
    assert "student logins" in sanitized
    assert "course completion" in sanitized

def test_data_driven_insights():
    # 3. Data-driven insights match calculated statistics
    df = pl.DataFrame({
        "Company": ["Dell", "Apple", "Dell", "HP"],
        "Cpu": ["Intel", "Apple", "Intel", "Intel"],
        "Ram": ["8GB", "16GB", "8GB", "8GB"],
        "Memory": ["256GB SSD", "512GB SSD", "1TB HDD", "128GB SSD"],
        "Gpu": ["Intel", "Apple", "Intel", "Intel"],
        "Price": [1000.0, 2000.0, 1200.0, 800.0],
        "OpSys": ["Windows 10", "macOS", "Windows 10", "Windows 11"]
    })
    
    schema = infer_schema(df, domain="Electronics")
    biz = generate_business_context(df, schema, domain="Electronics")
    
    ctx = biz["business_context"].lower()
    assert "apple" in ctx
    assert "windows 10" in ctx
    assert "ssd" in ctx
    assert "prevalent" in ctx
