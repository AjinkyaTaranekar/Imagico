from fastapi import APIRouter, File, UploadFile, status

from ..models.media_quality import MediaQuality
from ..services.media_service import MediaService

media_router = APIRouter(tags=["Media"])
media_service = MediaService()


@media_router.post("/uploadfiles/", status_code=status.HTTP_201_CREATED)
async def create_upload_files(
    files: list[UploadFile] = File(...),
):
    return await media_service.create_upload_files(files=files)


@media_router.get("/get/{filename}")
async def get_uploaded_file(
    filename: str,
    width: int = 0,
    height: int = 0,
    quality: MediaQuality = MediaQuality.original,
):
    return await media_service.get_uploaded_file(
        filename=filename, width=width, height=height, quality=quality
    )
