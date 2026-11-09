from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import MaintenanceRecord, Vehicle
from app.schemas import MaintenanceCreate


class MaintenanceConflictError(Exception):
    pass


def list_maintenance_records(
    session: Session, vehicle_id: int
) -> list[MaintenanceRecord] | None:
    if session.get(Vehicle, vehicle_id) is None:
        return None

    statement = (
        select(MaintenanceRecord)
        .where(MaintenanceRecord.vehicle_id == vehicle_id)
        .order_by(
            MaintenanceRecord.maintenance_date.desc(), MaintenanceRecord.id.desc()
        )
    )
    return list(session.scalars(statement))


def create_maintenance_record(
    session: Session, vehicle_id: int, record_data: MaintenanceCreate
) -> MaintenanceRecord | None:
    if session.get(Vehicle, vehicle_id) is None:
        return None

    record = MaintenanceRecord(vehicle_id=vehicle_id, **record_data.model_dump())
    session.add(record)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise MaintenanceConflictError from error

    session.refresh(record)
    return record


def update_maintenance_record(
    session: Session, maintenance_id: int, record_data: MaintenanceCreate
) -> MaintenanceRecord | None:
    record = session.get(MaintenanceRecord, maintenance_id)
    if record is None:
        return None

    for field_name, field_value in record_data.model_dump().items():
        setattr(record, field_name, field_value)

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise MaintenanceConflictError from error

    session.refresh(record)
    return record


def delete_maintenance_record(session: Session, maintenance_id: int) -> bool:
    record = session.get(MaintenanceRecord, maintenance_id)
    if record is None:
        return False

    session.delete(record)
    session.commit()
    return True
