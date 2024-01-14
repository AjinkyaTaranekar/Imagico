from typing import Annotated, Optional

from fastapi import APIRouter, File, Header, HTTPException, UploadFile, status

from ..constants.constants import DEFAULT_HEIGHT, DEFAULT_QUALITY, DEFAULT_WIDTH
from ..models.media_quality import MediaQuality
from ..services.media_service import MediaService

media_router = APIRouter(tags=["Media"])
media_service = MediaService()


@media_router.post("/uploadfiles/", status_code=status.HTTP_201_CREATED)
async def create_upload_files(files: list[UploadFile] = File(...)):
    await media_service.create_upload_files(files)
    return {"message": "Files uploaded successfully"}


@media_router.get("/{filename}")
async def get_image(
    filename: str,
    user_agent: Annotated[str | None, Header()] = None,
    width: Optional[int] = DEFAULT_WIDTH,
    height: Optional[int] = DEFAULT_HEIGHT,
    quality: Optional[MediaQuality] = DEFAULT_QUALITY,
    blur: Optional[bool] = False,
):
    try:
        return await media_service.get_uploaded_file(
            filename=filename,
            user_agent_string=user_agent,
            width=width,
            height=height,
            quality=quality,
            blur=blur,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}")
