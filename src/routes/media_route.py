from typing import Annotated

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status

from ..constants.constants import DEFAULT_HEIGHT, DEFAULT_QUALITY, DEFAULT_WIDTH
from ..models.media_quality import MediaQuality
from ..services.media_service import MediaService

media_router = APIRouter(tags=["Media"])
media_service = MediaService()


@media_router.post("/uploadfiles/", status_code=status.HTTP_201_CREATED)
async def create_upload_files(files: list[UploadFile] = File(...)):
    await media_service.create_upload_files(files)
    return {"message": "Files uploaded successfully"}


@media_router.get("/get/{filename}")
async def get_uploaded_file(
    filename: str,
    user_agent: Annotated[str | None, Header()] = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    quality: MediaQuality = DEFAULT_QUALITY,
    media_service: MediaService = Depends(),
):
    try:
        return await media_service.get_uploaded_file(
            filename=filename,
            user_agent_string=user_agent,
            width=width,
            height=height,
            quality=quality,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}")
