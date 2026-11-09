from fastapi import APIRouter

from app.config import is_demo_read_only
from app.schemas import DemoConfigurationResponse

router = APIRouter(prefix="/api/v1", tags=["configuration"])


@router.get("/config", response_model=DemoConfigurationResponse)
def read_configuration() -> DemoConfigurationResponse:
    return DemoConfigurationResponse(demo_read_only=is_demo_read_only())
