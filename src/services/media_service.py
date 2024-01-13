import json
import logging
from http import HTTPStatus
from pathlib import Path
from typing import Annotated

from fastapi import Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image
from requests import get
from user_agents import parse

from ..constants.constants import DEFAULT_HEIGHT, DEFAULT_QUALITY, DEFAULT_WIDTH
from ..models.media_quality import MediaQuality, MediaQualityCompression
from ..utils.directory import create_directory
from ..utils.file import clean_filename

UPLOAD_DIR = Path("uploads")
create_directory(UPLOAD_DIR)

# Fetch webp support data
WEBP_SUPPORT_URL = (
    "https://raw.githubusercontent.com/Fyrd/caniuse/main/features-json/webp.json"
)
webp_support = get(WEBP_SUPPORT_URL).json()

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
        user_agent_string: Annotated[str | None, Header()],
        width: int,
        height: int,
        quality: MediaQuality,
    ) -> FileResponse:
        try:
            filename = clean_filename(filename)
            user_agent = parse(user_agent_string)
            logging.info(user_agent)
            subdirectory = (
                UPLOAD_DIR / filename / str(width) / str(height) / quality.value
            )
            filepath = subdirectory / filename

            # Check if the browser supports WebP
            browser_name = user_agent.browser.family.lower()
            browser_version = user_agent.browser.version[0]
            webp_supported = (
                webp_support.get("stats", {})
                .get(browser_name, {})
                .get(str(browser_version))
                == "y"
            )
            filepath_webp = Path(f"{filepath}.webp")

            if not filepath.exists():
                original_filepath = (
                    UPLOAD_DIR
                    / filename
                    / str(DEFAULT_WIDTH)
                    / str(DEFAULT_HEIGHT)
                    / DEFAULT_QUALITY.value
                    / filename
                )
                if not original_filepath.exists():
                    raise FileNotFoundError(f"Original File Not found {filename}")
                create_directory(subdirectory)

                image = (
                    Image.open(original_filepath).convert("RGB").resize((width, height))
                )

                # Save the image with appropriate compression and optimization
                save_params = {
                    "optimize": True,
                    "quality": next(
                        (
                            member.value
                            for member in MediaQualityCompression
                            if member.name == quality
                        ),
                        MediaQualityCompression.original.value,
                    ),
                }

                if webp_supported:
                    image.save(filepath_webp, "webp", **save_params)
                else:
                    image.save(filepath, "JPEG", **save_params)

                logging.info(
                    f"Image created successfully in WebP format: {filename}"
                    if webp_supported
                    else f"Image created successfully: {filename}"
                )
            else:
                logging.info(f"Image found successfully: {filename}")
        except Exception as e:
            logging.error(f"Failed to create or retrieve image. Exception: {e}")
            raise HTTPException(500, "Failed to create or retrieve image")

        return FileResponse(filepath_webp) if webp_supported else FileResponse(filepath)
