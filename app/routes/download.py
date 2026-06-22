from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/exports", tags=["exports"])
EXPORT_DIR = Path("exports").resolve()


@router.get("/{file_name}")
def download_file(file_name: str) -> FileResponse:
    safe_name = Path(file_name).name
    path = EXPORT_DIR / safe_name
    if safe_name != file_name or not path.is_file():
        raise HTTPException(status_code=404, detail="Export not found")
    return FileResponse(path, filename=safe_name, media_type="text/csv")
