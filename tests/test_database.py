import pytest
import polars as pl
from unittest.mock import patch
from app.db.session import Base
from app.models.dataset import Dataset
from app.models.issue import QualityIssue
from app.models.audit_log import AuditLog
from app.services.dataset_store import save_dataset, get_dataset, delete_dataset, list_datasets

@pytest.fixture
def test_db(monkeypatch, tmp_path):
    # Use a temp sqlite db for testing
    db_file = tmp_path / "test_dataclean.db"
    db_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    
    # Re-bind engine for testing
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
    
    test_engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    
    test_session = scoped_session(sessionmaker(bind=test_engine))
    
    # Patch SessionLocal in app.db.session, app.services.dataset_store, and app.services.dashboard_service
    with patch("app.db.session.SessionLocal", test_session), \
         patch("app.services.dataset_store.SessionLocal", test_session), \
         patch("app.services.dashboard_service.SessionLocal", test_session):
        yield test_session
        
    Base.metadata.drop_all(bind=test_engine)

def test_db_persistence(test_db):
    df = pl.DataFrame({"A": [1, 2, 3]})
    
    # Save dataset via store service
    ds_id = save_dataset(df)
    assert ds_id is not None
    
    # Check it is in DB using the test_db fixture directly
    db_ds = test_db.query(Dataset).filter(Dataset.id == ds_id).first()
    assert db_ds is not None
    assert db_ds.id == ds_id
    assert db_ds.status == "uploaded"
    
    # Verify retrieval
    df_retrieved = get_dataset(ds_id)
    assert df_retrieved is not None
    assert df_retrieved.equals(df)
    
    # Verify list
    assert ds_id in list_datasets()
    
    # Verify delete
    delete_dataset(ds_id)
    db_ds_post_del = test_db.query(Dataset).filter(Dataset.id == ds_id).first()
    assert db_ds_post_del is None
