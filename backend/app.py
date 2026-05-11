from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.api.routers.device import router as device_router

project_root = Path(__file__).resolve().parents[1]
frontend_index = project_root / "frontend" / "index.html"

app = FastAPI(
    title="Yolobit IoT Backend",
    description="FastAPI backend for Yolobit IoT dashboard and device data ingestion.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    resources={r"/api/*": {"origins": ["*"]}},
)

app.include_router(device_router)
