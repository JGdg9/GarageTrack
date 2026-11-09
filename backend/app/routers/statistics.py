from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas import StatisticsResponse
from app.services.statistics import get_statistics

router = APIRouter(prefix="/api/v1", tags=["statistics"])


@router.get("/statistics", response_model=StatisticsResponse)
def read_statistics(
    session: Annotated[Session, Depends(get_session)],
) -> StatisticsResponse:
    return get_statistics(session)
