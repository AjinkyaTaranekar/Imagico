from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

media_router = APIRouter(tags=["Media"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@media_router.post("/uploadfiles/")
async def create_upload_files(
    files: list[UploadFile] = File(...),
):
    filenames = []
    for file in files:
        contents = await file.read()
        filepath = UPLOAD_DIR / file.filename
        with open(filepath, "wb") as f:
            f.write(contents)
        filenames.append(file.filename)
    return {"filenames": filenames}


@media_router.get("/get/{filename}")
async def get_uploaded_file(filename: str):
    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)
