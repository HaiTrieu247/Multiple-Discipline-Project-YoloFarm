from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers.device import router as device_router

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


@app.get("/", tags=["health"])
def root() -> dict:
    return {"message": "Yolobit IoT backend is running."}
