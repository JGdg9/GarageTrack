from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas import MaintenanceCreate, MaintenanceResponse
from app.services.maintenance import (
    MaintenanceConflictError,
    create_maintenance_record,
    delete_maintenance_record,
    list_maintenance_records,
    update_maintenance_record,
)

router = APIRouter(tags=["maintenance"])


@router.get(
    "/api/v1/vehicles/{vehicle_id}/maintenance",
    response_model=list[MaintenanceResponse],
)
def read_maintenance_history(
    vehicle_id: Annotated[int, Path(gt=0)],
    session: Annotated[Session, Depends(get_session)],
) -> list[MaintenanceResponse]:
    records = list_maintenance_records(session, vehicle_id)
    if records is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found."
        )
    return records


@router.post(
    "/api/v1/vehicles/{vehicle_id}/maintenance",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_maintenance_record(
    record_data: MaintenanceCreate,
    vehicle_id: Annotated[int, Path(gt=0)],
    session: Annotated[Session, Depends(get_session)],
) -> MaintenanceResponse:
    try:
        record = create_maintenance_record(session, vehicle_id, record_data)
    except MaintenanceConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The maintenance record conflicts with the current data.",
        ) from None

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found."
        )
    return record


@router.put("/api/v1/maintenance/{maintenance_id}", response_model=MaintenanceResponse)
def edit_maintenance_record(
    record_data: MaintenanceCreate,
    maintenance_id: Annotated[int, Path(gt=0)],
    session: Annotated[Session, Depends(get_session)],
) -> MaintenanceResponse:
    try:
        record = update_maintenance_record(session, maintenance_id, record_data)
    except MaintenanceConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The maintenance record conflicts with the current data.",
        ) from None

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found.",
        )
    return record


@router.delete(
    "/api/v1/maintenance/{maintenance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_maintenance_record(
    maintenance_id: Annotated[int, Path(gt=0)],
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    if not delete_maintenance_record(session, maintenance_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
