from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        CheckConstraint("year >= 1886", name="ck_vehicles_year"),
        CheckConstraint("current_mileage >= 0", name="ck_vehicles_current_mileage"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    license_plate: Mapped[str | None] = mapped_column(String(20), unique=True)
    current_mileage: Mapped[int] = mapped_column(Integer, nullable=False)
    maintenance_records: Mapped[list[MaintenanceRecord]] = relationship(
        back_populates="vehicle",
        passive_deletes="all",
    )


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"
    __table_args__ = (
        CheckConstraint("mileage >= 0", name="ck_maintenance_records_mileage"),
        CheckConstraint("cost >= 0", name="ck_maintenance_records_cost"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_0900_ai_ci",
        },
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=False)
    maintenance_date: Mapped[date] = mapped_column(Date, nullable=False)
    mileage: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    vehicle: Mapped[Vehicle] = relationship(back_populates="maintenance_records")
