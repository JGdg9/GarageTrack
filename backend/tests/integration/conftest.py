import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def vehicle_id(client: TestClient) -> int:
    response = client.post(
        "/api/v1/vehicles",
        json={
            "brand": "Honda",
            "model": "Civic",
            "year": 2022,
            "license_plate": "TEST 123",
            "current_mileage": 15000,
        },
    )

    assert response.status_code == 201
    return response.json()["id"]
