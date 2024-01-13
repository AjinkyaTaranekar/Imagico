from http import HTTPStatus
from pathlib import Path

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..models.media_quality import MediaQuality

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class MediaService:
    async def create_upload_files(self, files: list[UploadFile]):
        filenames = []
        for file in files:
            contents = await file.read()
            filepath = UPLOAD_DIR / file.filename
            with open(filepath, "wb") as f:
                f.write(contents)
            filenames.append(file.filename)
        return HTTPStatus.CREATED

    async def get_uploaded_file(
        self,
        filename: str,
        width: int,
        height: int,
        quality: MediaQuality,
    ) -> FileResponse:
        filepath = UPLOAD_DIR / filename
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(filepath)
