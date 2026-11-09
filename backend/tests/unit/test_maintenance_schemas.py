from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import MaintenanceCreate


def valid_maintenance_data(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "maintenance_type": "Oil change",
        "maintenance_date": "2025-03-14",
        "mileage": 45000,
        "cost": "125.50",
        "description": "Engine oil and filter",
    }
    data.update(overrides)
    return data


def test_maintenance_fields_are_normalized() -> None:
    maintenance = MaintenanceCreate(
        **valid_maintenance_data(
            maintenance_type="  Oil change  ",
            description="  Engine oil and filter  ",
        )
    )

    assert maintenance.maintenance_type == "Oil change"
    assert maintenance.maintenance_date == date(2025, 3, 14)
    assert isinstance(maintenance.cost, Decimal)
    assert maintenance.cost == Decimal("125.50")
    assert maintenance.description == "Engine oil and filter"


@pytest.mark.parametrize("maintenance_type", ["", " ", "\t"])
def test_maintenance_type_must_not_be_blank(maintenance_type: str) -> None:
    with pytest.raises(ValidationError):
        MaintenanceCreate(**valid_maintenance_data(maintenance_type=maintenance_type))


def test_maintenance_date_must_be_valid() -> None:
    with pytest.raises(ValidationError):
        MaintenanceCreate(**valid_maintenance_data(maintenance_date="2025-02-30"))


@pytest.mark.parametrize("mileage", [-1, -100])
def test_maintenance_mileage_must_not_be_negative(mileage: int) -> None:
    with pytest.raises(ValidationError):
        MaintenanceCreate(**valid_maintenance_data(mileage=mileage))


@pytest.mark.parametrize("cost", ["-0.01", "-100.00"])
def test_maintenance_cost_must_not_be_negative(cost: str) -> None:
    with pytest.raises(ValidationError):
        MaintenanceCreate(**valid_maintenance_data(cost=cost))


def test_maintenance_cost_allows_at_most_two_decimal_places() -> None:
    with pytest.raises(ValidationError):
        MaintenanceCreate(**valid_maintenance_data(cost="12.345"))


def test_blank_maintenance_description_is_treated_as_missing() -> None:
    maintenance = MaintenanceCreate(**valid_maintenance_data(description=" "))

    assert maintenance.description is None
