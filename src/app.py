from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .routes.media_route import media_router


app = FastAPI(
    title="Imagico",
    swagger_ui_parameters={
        "deepLinking": True,
        "requestSnippetsEnabled": True,
        "tryItOutEnabled": True,
        "requestSnippets": {
            "generators": {
                "curl_bash": {"title": "cURL (bash)", "syntax": "bash"},
                "curl_powershell": {
                    "title": "cURL (PowerShell)",
                    "syntax": "powershell",
                },
                "curl_cmd": {"title": "cURL (CMD)", "syntax": "bash"},
            },
            "defaultExpanded": True,
            "languages": None,
        },
    },
)
allow_all = ["*"]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=allow_all,
    allow_headers=allow_all,
)

app.include_router(media_router, prefix="/api/v1")

