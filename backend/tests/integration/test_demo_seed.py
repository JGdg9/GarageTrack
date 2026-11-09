from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import seed_demo
from app.models import MaintenanceRecord, Vehicle


def test_demo_seed_creates_sample_records_when_read_only(
    integration_engine, monkeypatch
) -> None:
    monkeypatch.setenv("DEMO_READ_ONLY", "true")
    monkeypatch.setattr(seed_demo, "get_engine", lambda: integration_engine)

    seed_demo.seed_demo_data()

    with Session(integration_engine) as session:
        vehicle_count = session.scalar(select(func.count()).select_from(Vehicle))
        maintenance_count = session.scalar(
            select(func.count()).select_from(MaintenanceRecord)
        )

    assert vehicle_count == 2
    assert maintenance_count == 3


def test_demo_seed_is_idempotent(integration_engine, monkeypatch) -> None:
    monkeypatch.setenv("DEMO_READ_ONLY", "true")
    monkeypatch.setattr(seed_demo, "get_engine", lambda: integration_engine)

    seed_demo.seed_demo_data()
    seed_demo.seed_demo_data()

    with Session(integration_engine) as session:
        vehicle_count = session.scalar(select(func.count()).select_from(Vehicle))
        maintenance_count = session.scalar(
            select(func.count()).select_from(MaintenanceRecord)
        )

    assert vehicle_count == 2
    assert maintenance_count == 3


def test_demo_seed_does_not_write_when_read_only_is_disabled(
    integration_engine, monkeypatch
) -> None:
    monkeypatch.setenv("DEMO_READ_ONLY", "false")
    monkeypatch.setattr(seed_demo, "get_engine", lambda: integration_engine)

    seed_demo.seed_demo_data()

    with Session(integration_engine) as session:
        vehicle_count = session.scalar(select(func.count()).select_from(Vehicle))

    assert vehicle_count == 0
