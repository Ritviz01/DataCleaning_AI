import os
import uuid
import time
import threading
from pathlib import Path
import polars as pl
from app.services.dataset_reader import read_dataset
from app.services.file_detector import detect_file_type
from app.services.column_cleaner import clean_column_names
from app.db.session import SessionLocal
from app.models.dataset import Dataset
from app.models.issue import QualityIssue
from app.models.audit_log import AuditLog

class DatasetStore:
    """Thread-safe memory store for tabular datasets with database persistence and disk fallbacks."""
    def __init__(self, upload_dir: str = "uploads", expiry_seconds: int = 86400):
        self._cache = {}
        self._filepaths = {}
        self._timestamps = {}
        self._lock = threading.Lock()
        self.upload_dir = Path(upload_dir).resolve()
        self.expiry_seconds = expiry_seconds

    def _cleanup_expired(self) -> None:
        """Removes datasets that have exceeded their idle lifespan from in-memory cache."""
        now = time.time()
        expired_ids = [
            ds_id for ds_id, ts in self._timestamps.items()
            if now - ts > self.expiry_seconds
        ]
        for ds_id in expired_ids:
            self._cache.pop(ds_id, None)
            self._filepaths.pop(ds_id, None)
            self._timestamps.pop(ds_id, None)

    def store(
        self,
        dataframe: pl.DataFrame,
        file_path: str | Path | None = None,
        dataset_id: str | None = None,
        status: str = "uploaded",
        quality_score: float | None = None,
        issues: list | None = None,
        audit_logs: list | None = None
    ) -> str:
        """Stores a dataframe in the cache and associates it with a unique ID, persisting metadata in the DB."""
        with self._lock:
            self._cleanup_expired()
            if not dataset_id:
                dataset_id = uuid.uuid4().hex[:12]
            self._cache[dataset_id] = dataframe
            self._timestamps[dataset_id] = time.time()
            
            resolved_path = None
            filename = None
            if file_path:
                resolved_path = str(Path(file_path).resolve())
                self._filepaths[dataset_id] = resolved_path
                filename = Path(resolved_path).name

            # Persist metadata in database
            db = SessionLocal()
            try:
                db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
                if not db_dataset:
                    db_dataset = Dataset(
                        id=dataset_id,
                        filename=filename,
                        file_path=resolved_path,
                        status=status,
                        quality_score=quality_score
                    )
                    db.add(db_dataset)
                else:
                    if resolved_path:
                        db_dataset.file_path = resolved_path
                        db_dataset.filename = filename
                    db_dataset.status = status
                    db_dataset.quality_score = quality_score
                
                # Store issues if provided
                if issues is not None:
                    db.query(QualityIssue).filter(QualityIssue.dataset_id == dataset_id).delete()
                    for issue in issues:
                        col = issue.get("column") or issue.get("column_name")
                        db_issue = QualityIssue(
                            dataset_id=dataset_id,
                            column_name=col,
                            issue_type=issue.get("issue_type"),
                            original_value=str(issue.get("original_value")) if issue.get("original_value") is not None else None,
                            confidence=issue.get("confidence"),
                            recommendation=issue.get("recommendation"),
                            status=issue.get("status", "proposed")
                        )
                        db.add(db_issue)
                
                # Store audit logs if provided
                if audit_logs is not None:
                    db.query(AuditLog).filter(AuditLog.dataset_id == dataset_id).delete()
                    for log in audit_logs:
                        col = log.get("column") or log.get("column_name")
                        db_log = AuditLog(
                            dataset_id=dataset_id,
                            column_name=col,
                            action_taken=log.get("action_taken"),
                            old_value=str(log.get("old_value")) if log.get("old_value") is not None else None,
                            new_value=str(log.get("new_value")) if log.get("new_value") is not None else None
                        )
                        db.add(db_log)

                db.commit()
            except Exception as e:
                print(f"Error persisting dataset metadata to DB: {e}")
                db.rollback()
            finally:
                db.close()
            return dataset_id

    def get(self, dataset_id: str) -> pl.DataFrame | None:
        """Retrieves a dataframe by ID, loading it from disk using DB metadata or file paths."""
        with self._lock:
            self._cleanup_expired()
            if dataset_id in self._cache:
                self._timestamps[dataset_id] = time.time()
                return self._cache[dataset_id]

            # Try to resolve path from filepaths dict
            file_path = self._filepaths.get(dataset_id)
            
            # If not in filepaths dict, look up in database
            if not file_path:
                db = SessionLocal()
                try:
                    db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
                    if db_dataset:
                        file_path = db_dataset.file_path
                        self._filepaths[dataset_id] = file_path
                except Exception as e:
                    print(f"Error loading dataset metadata from DB: {e}")
                finally:
                    db.close()
            
            # If still not in filepaths dict, look up in uploads folder
            if not file_path and self.upload_dir.exists():
                for item in self.upload_dir.iterdir():
                    if item.is_file() and item.name.startswith(f"{dataset_id}_"):
                        file_path = str(item.resolve())
                        break
            
            if file_path and os.path.exists(file_path):
                try:
                    file_type = detect_file_type(file_path)
                    if file_type != "unknown":
                        df = clean_column_names(read_dataset(file_path, file_type))
                        self._cache[dataset_id] = df
                        self._filepaths[dataset_id] = file_path
                        self._timestamps[dataset_id] = time.time()
                        return df
                except Exception as e:
                    print(f"Error restoring dataset {dataset_id} from {file_path}: {e}")
                    return None

            return None

    def delete(self, dataset_id: str) -> bool:
        """Removes a dataset from the cache, tracked filepaths, and database."""
        with self._lock:
            self._cleanup_expired()
            existed = dataset_id in self._cache or dataset_id in self._filepaths
            self._cache.pop(dataset_id, None)
            self._filepaths.pop(dataset_id, None)
            self._timestamps.pop(dataset_id, None)
            
            # Delete from DB
            db = SessionLocal()
            try:
                db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
                if db_dataset:
                    db.delete(db_dataset)
                    db.commit()
                    existed = True
            except Exception as e:
                print(f"Error deleting dataset from DB: {e}")
                db.rollback()
            finally:
                db.close()
            return existed

    def list_ids(self) -> list[str]:
        """Lists all currently tracked dataset IDs in memory and database."""
        with self._lock:
            self._cleanup_expired()
            ids = set(self._cache.keys()) | set(self._filepaths.keys())
            db = SessionLocal()
            try:
                db_ids = [d.id for d in db.query(Dataset.id).all()]
                ids.update(db_ids)
            except Exception as e:
                print(f"Error listing dataset IDs from DB: {e}")
            finally:
                db.close()
            return list(ids)

# Singleton instance
dataset_store = DatasetStore()

# Required module-level functions
def save_dataset(df: pl.DataFrame) -> str:
    """Generate unique dataset ID and store dataframe in memory/DB."""
    return dataset_store.store(df)

def get_dataset(dataset_id: str) -> pl.DataFrame | None:
    """Retrieve dataframe by dataset ID."""
    return dataset_store.get(dataset_id)

def delete_dataset(dataset_id: str) -> bool:
    """Delete a dataset from memory/DB."""
    return dataset_store.delete(dataset_id)

def list_datasets() -> list[str]:
    """List all available datasets."""
    return dataset_store.list_ids()
