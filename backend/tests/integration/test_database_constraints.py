from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.models import MaintenanceRecord, Vehicle


def create_vehicle(session: Session, current_mileage: int = 15000) -> Vehicle:
    vehicle = Vehicle(
        brand="Honda",
        model="Civic",
        year=2022,
        license_plate="CHECK 123",
        current_mileage=current_mileage,
    )
    session.add(vehicle)
    session.commit()
    return vehicle


def test_mysql_rejects_maintenance_for_missing_vehicle(integration_engine) -> None:
    with Session(integration_engine) as session:
        record = MaintenanceRecord(
            vehicle_id=999999,
            maintenance_type="Oil change",
            maintenance_date=date(2026, 1, 15),
            mileage=15000,
            cost=Decimal("89.95"),
        )
        session.add(record)

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()


def test_mysql_rejects_negative_vehicle_mileage(integration_engine) -> None:
    with Session(integration_engine) as session:
        vehicle = Vehicle(
            brand="Honda",
            model="Civic",
            year=2022,
            current_mileage=-1,
        )
        session.add(vehicle)

        with pytest.raises(OperationalError):
            session.commit()

        session.rollback()


def test_mysql_rejects_negative_maintenance_mileage(integration_engine) -> None:
    with Session(integration_engine) as session:
        vehicle = create_vehicle(session)
        record = MaintenanceRecord(
            vehicle_id=vehicle.id,
            maintenance_type="Oil change",
            maintenance_date=date(2026, 1, 15),
            mileage=-1,
            cost=Decimal("89.95"),
        )
        session.add(record)

        with pytest.raises(OperationalError):
            session.commit()

        session.rollback()


def test_mysql_rejects_negative_maintenance_cost(integration_engine) -> None:
    with Session(integration_engine) as session:
        vehicle = create_vehicle(session)
        record = MaintenanceRecord(
            vehicle_id=vehicle.id,
            maintenance_type="Oil change",
            maintenance_date=date(2026, 1, 15),
            mileage=15000,
            cost=Decimal("-0.01"),
        )
        session.add(record)

        with pytest.raises(OperationalError):
            session.commit()

        session.rollback()


def test_mysql_restricts_vehicle_deletion_with_maintenance(integration_engine) -> None:
    with Session(integration_engine) as session:
        vehicle = create_vehicle(session)
        record = MaintenanceRecord(
            vehicle_id=vehicle.id,
            maintenance_type="Oil change",
            maintenance_date=date(2026, 1, 15),
            mileage=15000,
            cost=Decimal("89.95"),
        )
        session.add(record)
        session.commit()
        session.delete(vehicle)

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()
