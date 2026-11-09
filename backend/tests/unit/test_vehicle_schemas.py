from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas import VehicleCreate


def test_vehicle_text_fields_are_normalized() -> None:
    vehicle = VehicleCreate(
        brand=" Honda ",
        model=" Civic ",
        year=2022,
        license_plate=" 123 abc ",
        current_mileage=15000,
    )

    assert vehicle.brand == "Honda"
    assert vehicle.model == "Civic"
    assert vehicle.license_plate == "123 ABC"


@pytest.mark.parametrize("brand", ["", " ", "\t"])
def test_vehicle_brand_must_not_be_blank(brand: str) -> None:
    with pytest.raises(ValidationError):
        VehicleCreate(
            brand=brand,
            model="Civic",
            year=2022,
            current_mileage=15000,
        )


@pytest.mark.parametrize("model", ["", " ", "\t"])
def test_vehicle_model_must_not_be_blank(model: str) -> None:
    with pytest.raises(ValidationError):
        VehicleCreate(
            brand="Honda",
            model=model,
            year=2022,
            current_mileage=15000,
        )


@pytest.mark.parametrize("year", [1885, date.today().year + 2])
def test_vehicle_year_must_be_reasonable(year: int) -> None:
    with pytest.raises(ValidationError):
        VehicleCreate(
            brand="Honda",
            model="Civic",
            year=year,
            current_mileage=15000,
        )


@pytest.mark.parametrize("current_mileage", [-1, -100])
def test_vehicle_mileage_must_not_be_negative(current_mileage: int) -> None:
    with pytest.raises(ValidationError):
        VehicleCreate(
            brand="Honda",
            model="Civic",
            year=2022,
            current_mileage=current_mileage,
        )


@pytest.mark.parametrize("license_plate", ["", " ", "\t"])
def test_blank_license_plate_is_treated_as_missing(license_plate: str) -> None:
    vehicle = VehicleCreate(
        brand="Honda",
        model="Civic",
        year=2022,
        license_plate=license_plate,
        current_mileage=15000,
    )

    assert vehicle.license_plate is None


def test_vehicle_license_plate_is_optional() -> None:
    vehicle = VehicleCreate(
        brand="Honda",
        model="Civic",
        year=2022,
        current_mileage=15000,
    )

    assert vehicle.license_plate is None
