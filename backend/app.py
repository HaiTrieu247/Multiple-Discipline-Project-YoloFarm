from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from api.routers.device import router as device_router

project_root = Path(__file__).resolve().parents[1]
dist_dir = project_root / "frontend" / "dist"

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
)

app.include_router(device_router)


@app.get("/")
def serve_root():
    index = dist_dir / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({
        "message": "Backend is running. Build the frontend first.",
        "hint": "cd frontend && npm run build",
        "api_docs": "/docs",
    })


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    # Try to serve exact static file (JS, CSS, images…)
    candidate = dist_dir / full_path
    if candidate.is_file():
        return FileResponse(str(candidate))
    # Fall back to index.html so React Router handles the path client-side
    index = dist_dir / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"detail": "Not found"}, status_code=404)
