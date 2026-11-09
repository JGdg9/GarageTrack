from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import init_db, seed_demo, startup
from app.models import MaintenanceRecord, Vehicle


def test_startup_prepares_mysql_and_seeds_public_demo(
    integration_engine, monkeypatch
) -> None:
    monkeypatch.setenv("DEMO_READ_ONLY", "true")
    monkeypatch.setattr(startup, "get_engine", lambda: integration_engine)
    monkeypatch.setattr(init_db, "get_engine", lambda: integration_engine)
    monkeypatch.setattr(seed_demo, "get_engine", lambda: integration_engine)

    startup.prepare_database()

    with Session(integration_engine) as session:
        vehicle_count = session.scalar(select(func.count()).select_from(Vehicle))
        maintenance_count = session.scalar(
            select(func.count()).select_from(MaintenanceRecord)
        )

    assert vehicle_count == 2
    assert maintenance_count == 3
