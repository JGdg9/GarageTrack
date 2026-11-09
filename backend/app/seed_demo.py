from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import is_demo_read_only
from app.database import get_engine
from app.models import MaintenanceRecord, Vehicle


def seed_demo_data() -> None:
    if not is_demo_read_only():
        return

    with Session(get_engine()) as session, session.begin():
        existing_vehicle_id = session.scalar(select(Vehicle.id).limit(1))
        if existing_vehicle_id is not None:
            return

        vehicles = [
            Vehicle(
                brand="Toyota",
                model="Corolla",
                year=2020,
                license_plate=None,
                current_mileage=68400,
            ),
            Vehicle(
                brand="Volvo",
                model="V40",
                year=2018,
                license_plate=None,
                current_mileage=92750,
            ),
        ]
        session.add_all(vehicles)
        session.flush()
        session.add_all(
            [
                MaintenanceRecord(
                    vehicle_id=vehicles[0].id,
                    maintenance_type="Oil and filter change",
                    maintenance_date=date(2025, 3, 12),
                    mileage=61500,
                    cost=Decimal("124.90"),
                    description="Scheduled service",
                ),
                MaintenanceRecord(
                    vehicle_id=vehicles[0].id,
                    maintenance_type="Brake pads",
                    maintenance_date=date(2025, 10, 18),
                    mileage=66200,
                    cost=Decimal("289.50"),
                    description="Front brake pads replaced",
                ),
                MaintenanceRecord(
                    vehicle_id=vehicles[1].id,
                    maintenance_type="Tire replacement",
                    maintenance_date=date(2025, 6, 4),
                    mileage=90100,
                    cost=Decimal("476.00"),
                    description="Set of four tires",
                ),
            ]
        )
