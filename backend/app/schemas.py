from datetime import date

from pydantic import BaseModel, Field, field_validator

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
    maintenance_type: str
    maintenance_date: date
    mileage: int
    cost: float
    description: str | None = None
