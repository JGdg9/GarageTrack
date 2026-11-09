from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MIN_VEHICLE_YEAR = 1886
MAX_VEHICLE_YEAR = date.today().year + 1


class VehicleCreate(BaseModel):
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=MIN_VEHICLE_YEAR, le=MAX_VEHICLE_YEAR)
    license_plate: str | None = Field(default=None, max_length=20)
    current_mileage: int = Field(ge=0)

    @field_validator("brand", "model")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("This field cannot be blank.")
        return normalized_value

    @field_validator("license_plate", mode="before")
    @classmethod
    def normalize_license_plate(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_value = value.strip().upper()
        return normalized_value or None


class MaintenanceCreate(BaseModel):
    maintenance_type: str = Field(min_length=1, max_length=100)
    maintenance_date: date
    mileage: int = Field(ge=0)
    cost: Decimal = Field(ge=Decimal("0.00"), max_digits=10, decimal_places=2)
    description: str | None = None

    @field_validator("maintenance_type")
    @classmethod
    def normalize_maintenance_type(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("Maintenance type cannot be blank.")
        return normalized_value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_value = value.strip()
        return normalized_value or None


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    model: str
    year: int
    license_plate: str | None
    current_mileage: int


class MaintenanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: int
    maintenance_type: str
    maintenance_date: date
    mileage: int
    cost: Decimal
    description: str | None


class VehicleExpenseResponse(BaseModel):
    vehicle_id: int
    brand: str
    model: str
    total_expenses: Decimal


class StatisticsResponse(BaseModel):
    total_vehicles: int
    total_maintenance_records: int
    total_expenses: Decimal
    vehicle_expenses: list[VehicleExpenseResponse]


class DemoConfigurationResponse(BaseModel):
    demo_read_only: bool
