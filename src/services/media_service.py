import logging
from http import HTTPStatus
from pathlib import Path

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from wand.image import Image

from ..constants.constants import DEFAULT_HEIGHT, DEFAULT_QUALITY, DEFAULT_WIDTH
from ..models.media_quality import MediaQuality, MediaQualityCompression
from ..utils.directory import create_directory
from ..utils.file import clean_filename

UPLOAD_DIR = Path("uploads")
create_directory(UPLOAD_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class MediaService:
    async def create_upload_files(self, files: list[UploadFile]):
        try:
            for file in files:
                contents = await file.read()
                filename = clean_filename(file.filename)
                subdirectory = (
                    UPLOAD_DIR
                    / filename
                    / str(DEFAULT_WIDTH)
                    / str(DEFAULT_HEIGHT)
                    / DEFAULT_QUALITY.value
                )
                create_directory(subdirectory)

                filepath = subdirectory / filename
                with open(filepath, "wb") as f:
                    f.write(contents)
                logging.info(f"File uploaded successfully: {filename}")
        except Exception as e:
            logging.error(f"Failed to upload image. Exception: {e}")
            raise HTTPException(500, "Failed to upload image")
        return HTTPStatus.CREATED

    async def get_uploaded_file(
        self,
        filename: str,
        width: int,
        height: int,
        quality: MediaQuality,
    ) -> FileResponse:
        try:
            filename = clean_filename(filename)
            subdirectory = (
                UPLOAD_DIR / filename / str(width) / str(height) / quality.value
            )
            filepath = subdirectory / filename

            if not filepath.exists():
                original_filepath = (
                    UPLOAD_DIR
                    / filename
                    / str(DEFAULT_WIDTH)
                    / str(DEFAULT_HEIGHT)
                    / DEFAULT_QUALITY.value
                    / filename
                )
                create_directory(subdirectory)
                with Image(filename=original_filepath) as img:
                    img.resize(width, height)
                    img.compression_quality = MediaQualityCompression[
                        quality.value
                    ].value
                    img.save(filename=filepath)
                logging.info(f"Image created successfully: {filename}")
            else:
                logging.info(f"Image found successfully: {filename}")
        except Exception as e:
            logging.error(f"Failed to create or retrieve image. Exception: {e}")
            raise HTTPException(500, "Failed to create or retrieve image")

        return FileResponse(filepath)
