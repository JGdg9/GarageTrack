from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers.maintenance import router as maintenance_router
from app.routers.statistics import router as statistics_router
from app.routers.vehicles import router as vehicles_router

app = FastAPI(title="GarageTrack", version="1.0.0")
app.include_router(vehicles_router)
app.include_router(maintenance_router)
app.include_router(statistics_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


FRONTEND_PATH = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_PATH, html=True), name="frontend")
