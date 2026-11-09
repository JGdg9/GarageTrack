import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session

from app.database import get_session
from app.main import app
from app.models import Base


@pytest.fixture
def integration_engine() -> Iterator[Engine]:
    test_database_url = os.getenv("TEST_DATABASE_URL")
    if not test_database_url:
        raise RuntimeError("TEST_DATABASE_URL is not configured.")
    database_url = make_url(test_database_url)
    if database_url.database != "garagetrack_test":
        raise RuntimeError("Integration tests require the garagetrack_test database.")
    if database_url.drivername != "mysql+pymysql":
        raise RuntimeError("Integration tests require MySQL with the PyMySQL driver.")
    if database_url.host not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("Integration tests require a local MySQL server.")

    engine = create_engine(test_database_url, pool_pre_ping=True)
    try:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(integration_engine: Engine) -> Iterator[TestClient]:
    def get_test_session() -> Iterator[Session]:
        with Session(integration_engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_session, None)
