from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas import VehicleCreate, VehicleExpenseResponse, VehicleResponse
from app.services.vehicles import (
    DuplicateLicensePlateError,
    VehicleHasMaintenanceError,
    calculate_vehicle_expenses,
    create_vehicle,
    delete_vehicle,
    get_vehicle,
    list_vehicles,
    update_vehicle,
)

router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleResponse])
def read_vehicles(
    session: Annotated[Session, Depends(get_session)],
) -> list[VehicleResponse]:
    return list_vehicles(session)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def read_vehicle(
    vehicle_id: Annotated[int, Path(gt=0)],
    session: Annotated[Session, Depends(get_session)],
) -> VehicleResponse:
    vehicle = get_vehicle(session, vehicle_id)
    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found."
        )
    return vehicle


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def add_vehicle(
    vehicle_data: VehicleCreate, session: Annotated[Session, Depends(get_session)]
) -> VehicleResponse:
    try:
        return create_vehicle(session, vehicle_data)
    except DuplicateLicensePlateError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="License plate is already registered.",
        ) from None


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def edit_vehicle(
    vehicle_data: VehicleCreate,
    vehicle_id: Annotated[int, Path(gt=0)],
    session: Annotated[Session, Depends(get_session)],
) -> VehicleResponse:
    try:
        vehicle = update_vehicle(session, vehicle_id, vehicle_data)
    except DuplicateLicensePlateError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="License plate is already registered.",
        ) from None

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found."
        )
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_vehicle(
    vehicle_id: Annotated[int, Path(gt=0)],
    session: Annotated[Session, Depends(get_session)],
) -> Response:
    vehicle = get_vehicle(session, vehicle_id)
    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found."
        )

    try:
        delete_vehicle(session, vehicle)
    except VehicleHasMaintenanceError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Delete maintenance records before deleting this vehicle.",
        ) from None

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{vehicle_id}/expenses", response_model=VehicleExpenseResponse)
def read_vehicle_expenses(
    vehicle_id: Annotated[int, Path(gt=0)],
    session: Annotated[Session, Depends(get_session)],
) -> VehicleExpenseResponse:
    vehicle = get_vehicle(session, vehicle_id)
    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found."
        )

    return VehicleExpenseResponse(
        vehicle_id=vehicle.id,
        brand=vehicle.brand,
        model=vehicle.model,
        total_expenses=calculate_vehicle_expenses(session, vehicle_id),
    )
