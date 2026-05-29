from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/download/{filename}")
async def download_file(filename: str):

    file_path = f"transcripts/{filename}"

    return FileResponse(

        path=file_path,

        filename=filename,

        media_type='application/octet-stream'

    )