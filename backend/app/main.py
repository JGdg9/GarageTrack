from fastapi import FastAPI

app = FastAPI(title="GarageTrack", version="1.0.0")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
