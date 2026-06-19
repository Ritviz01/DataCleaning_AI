from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get(
    "/download/{file_name}"
)
def download_file(
    file_name: str
):

    path = (
        f"exports/{file_name}"
    )

    return FileResponse(
        path=path,
        filename=file_name,
        media_type=
        "application/octet-stream"
    )