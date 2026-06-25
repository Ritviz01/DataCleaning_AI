import os
import uuid
import threading
from pathlib import Path
import polars as pl
from app.services.dataset_reader import read_dataset
from app.services.file_detector import detect_file_type
from app.services.column_cleaner import clean_column_names

class DatasetStore:
    def __init__(self, upload_dir: str = "uploads"):
        self._cache = {}
        self._filepaths = {}
        self._lock = threading.Lock()
        self.upload_dir = Path(upload_dir).resolve()

    def store(self, dataframe: pl.DataFrame, file_path: str | Path | None = None, dataset_id: str | None = None) -> str:
        """Stores a dataframe in the cache and associates it with a unique ID."""
        with self._lock:
            if not dataset_id:
                dataset_id = uuid.uuid4().hex[:12]
            self._cache[dataset_id] = dataframe
            if file_path:
                self._filepaths[dataset_id] = str(Path(file_path).resolve())
            return dataset_id

    def get(self, dataset_id: str) -> pl.DataFrame | None:
        """Retrieves a dataframe by ID, loading it from disk if not in cache."""
        with self._lock:
            if dataset_id in self._cache:
                return self._cache[dataset_id]

            # Try to resolve path from filepaths dict
            file_path = self._filepaths.get(dataset_id)
            
            # If not in filepaths dict, look up in uploads folder
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
                        return df
                except Exception as e:
                    # Log error or print
                    print(f"Error restoring dataset {dataset_id} from {file_path}: {e}")
                    return None

            return None

# Singleton instance
dataset_store = DatasetStore()
