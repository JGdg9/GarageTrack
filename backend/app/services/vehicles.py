from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import MaintenanceRecord, Vehicle
from app.schemas import VehicleCreate


class DuplicateLicensePlateError(Exception):
    pass


class VehicleHasMaintenanceError(Exception):
    pass


def list_vehicles(session: Session) -> list[Vehicle]:
    statement = select(Vehicle).order_by(Vehicle.brand, Vehicle.model, Vehicle.id)
    return list(session.scalars(statement))


def get_vehicle(session: Session, vehicle_id: int) -> Vehicle | None:
    return session.get(Vehicle, vehicle_id)


def create_vehicle(session: Session, vehicle_data: VehicleCreate) -> Vehicle:
    vehicle = Vehicle(**vehicle_data.model_dump())
    session.add(vehicle)
    return save_vehicle(session, vehicle)


def update_vehicle(
    session: Session, vehicle_id: int, vehicle_data: VehicleCreate
) -> Vehicle | None:
    vehicle = session.get(Vehicle, vehicle_id)
    if vehicle is None:
        return None

    for field_name, field_value in vehicle_data.model_dump().items():
        setattr(vehicle, field_name, field_value)

    return save_vehicle(session, vehicle)


def delete_vehicle(session: Session, vehicle: Vehicle) -> None:
    if vehicle.maintenance_records:
        raise VehicleHasMaintenanceError

    session.delete(vehicle)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise VehicleHasMaintenanceError from error


def calculate_vehicle_expenses(session: Session, vehicle_id: int) -> Decimal:
    statement = select(func.coalesce(func.sum(MaintenanceRecord.cost), Decimal("0.00")))
    statement = statement.where(MaintenanceRecord.vehicle_id == vehicle_id)
    return session.scalar(statement) or Decimal("0.00")


def save_vehicle(session: Session, vehicle: Vehicle) -> Vehicle:
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DuplicateLicensePlateError from error

    session.refresh(vehicle)
    return vehicle
