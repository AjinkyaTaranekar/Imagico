import logging
from http import HTTPStatus
from pathlib import Path
from typing import Annotated, Optional

from fastapi import Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, ImageEnhance, ImageFilter
from requests import get
from user_agents import parse

from ..constants.constants import DEFAULT_HEIGHT, DEFAULT_QUALITY, DEFAULT_WIDTH
from ..models.media_quality import MediaQuality, MediaQualityCompression
from ..utils.directory import create_directory
from ..utils.file import clean_filename

UPLOAD_DIR = Path("uploads")
create_directory(UPLOAD_DIR)

WEBP_SUPPORT_URL = (
    "https://raw.githubusercontent.com/Fyrd/caniuse/main/features-json/webp.json"
)
webp_support = get(WEBP_SUPPORT_URL).json()

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
        width: Optional[int],
        height: Optional[int],
        quality: Optional[MediaQuality],
        blur: Optional[bool],
    ) -> FileResponse:
        try:
            filename = clean_filename(filename)
            user_agent = parse(user_agent_string)

            original_filepath = (
                UPLOAD_DIR
                / filename
                / str(DEFAULT_WIDTH)
                / str(DEFAULT_HEIGHT)
                / DEFAULT_QUALITY.value
                / filename
            )

            subdirectory = (
                UPLOAD_DIR / filename / str(width) / str(height) / quality.value
            )
            filepath = subdirectory / filename

            webp_supported = self.is_webp_supported(user_agent)

            if not filepath.exists() or (
                webp_supported and not filepath.with_suffix(".webp").exists()
            ):
                self.process_image(
                    original_filepath,
                    filepath,
                    width,
                    height,
                    MediaQualityCompression[quality.value].value,
                    blur,
                    webp_supported,
                )

            if webp_supported:
                filepath = filepath.with_suffix(".webp")
                return FileResponse(
                    filepath, headers={"Content-Disposition": f"filename={filename}"}
                )
            else:
                logging.info(f"Image found successfully: {filename}")
                return FileResponse(
                    original_filepath,
                    headers={"Content-Disposition": f"filename={filename}"},
                )
        except Exception as e:
            logging.error(
                f"Failed to create or retrieve image. Exception: {e}. Returning Original File"
            )
            return FileResponse(
                original_filepath,
                headers={"Content-Disposition": f"filename={filename}"},
            )

    def is_webp_supported(self, user_agent):
        browser_name = user_agent.browser.family.lower()
        browser_version = user_agent.browser.version[0]
        return (
            webp_support.get("stats", {})
            .get(browser_name, {})
            .get(str(browser_version))
            == "y"
        )

    def process_image(
        self,
        original_filepath,
        filepath,
        width,
        height,
        quality,
        blur,
        webp_supported,
    ):
        create_directory(filepath.parent)

        image = Image.open(original_filepath)

        if width and height:
            image = image.resize((width, height))
        elif width:
            image = image.resize((width, int(image.height * width / image.width)))
        elif height:
            image = image.resize((int(image.width * height / image.height), height))

        if blur:
            image = image.filter(ImageFilter.BLUR)

        if webp_supported:
            image.save(
                filepath.with_suffix(".webp"),
                format="webp",
                subsampling=0,
                quality=quality,
            )
        else:
            image.save(filepath, format="PNG", subsampling=0, quality=quality)

        logging.info(
            f"Image created successfully in WebP format: {original_filepath}"
            if webp_supported
            else f"Image created successfully: {original_filepath}"
        )
