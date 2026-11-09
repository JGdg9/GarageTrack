import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.database import get_session
from app.main import app
from app.models import Base


@pytest.fixture
def client() -> Iterator[TestClient]:
    test_database_url = os.getenv("TEST_DATABASE_URL")
    if not test_database_url:
        raise RuntimeError("TEST_DATABASE_URL is not configured.")
    if make_url(test_database_url).database != "garagetrack_test":
        raise RuntimeError("Integration tests require the garagetrack_test database.")

    engine = create_engine(test_database_url, pool_pre_ping=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def get_test_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_session, None)
        Base.metadata.drop_all(engine)
        engine.dispose()
