from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import MaintenanceRecord, Vehicle
from app.schemas import StatisticsResponse, VehicleExpenseResponse


def get_statistics(session: Session) -> StatisticsResponse:
    total_vehicles = session.scalar(select(func.count(Vehicle.id))) or 0
    total_maintenance_records = (
        session.scalar(select(func.count(MaintenanceRecord.id))) or 0
    )
    total_expenses = session.scalar(
        select(func.coalesce(func.sum(MaintenanceRecord.cost), Decimal("0.00")))
    ) or Decimal("0.00")

    vehicle_expenses_statement = (
        select(
            Vehicle.id.label("vehicle_id"),
            Vehicle.brand,
            Vehicle.model,
            func.coalesce(func.sum(MaintenanceRecord.cost), Decimal("0.00")).label(
                "total_expenses"
            ),
        )
        .outerjoin(MaintenanceRecord, MaintenanceRecord.vehicle_id == Vehicle.id)
        .group_by(Vehicle.id)
        .order_by(Vehicle.brand, Vehicle.model, Vehicle.id)
    )
    vehicle_expenses = [
        VehicleExpenseResponse(**row._mapping)
        for row in session.execute(vehicle_expenses_statement)
    ]

    return StatisticsResponse(
        total_vehicles=total_vehicles,
        total_maintenance_records=total_maintenance_records,
        total_expenses=total_expenses,
        vehicle_expenses=vehicle_expenses,
    )
