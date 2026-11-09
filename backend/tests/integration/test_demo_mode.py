import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    ("method", "endpoint", "request_data"),
    [
        (
            "post",
            "/api/v1/vehicles",
            {
                "brand": "Honda",
                "model": "Civic",
                "year": 2022,
                "current_mileage": 1000,
            },
        ),
        (
            "put",
            "/api/v1/vehicles/1",
            {
                "brand": "Honda",
                "model": "Civic",
                "year": 2022,
                "current_mileage": 1000,
            },
        ),
        ("delete", "/api/v1/vehicles/1", None),
        (
            "post",
            "/api/v1/vehicles/1/maintenance",
            {
                "maintenance_type": "Oil change",
                "maintenance_date": "2026-04-12",
                "mileage": 1000,
                "cost": "89.95",
            },
        ),
        (
            "put",
            "/api/v1/maintenance/1",
            {
                "maintenance_type": "Oil change",
                "maintenance_date": "2026-04-12",
                "mileage": 1000,
                "cost": "89.95",
            },
        ),
        ("delete", "/api/v1/maintenance/1", None),
    ],
)
def test_read_only_demo_rejects_all_mutations(
    client: TestClient,
    monkeypatch,
    method: str,
    endpoint: str,
    request_data: dict | None,
) -> None:
    monkeypatch.setenv("DEMO_READ_ONLY", "true")
    request_method = getattr(client, method)
    response = (
        request_method(endpoint, json=request_data)
        if request_data
        else request_method(endpoint)
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "The public demo is read-only."}


def test_demo_configuration_reports_read_only_mode(
    client: TestClient, monkeypatch
) -> None:
    monkeypatch.setenv("DEMO_READ_ONLY", "true")

    response = client.get("/api/v1/config")

    assert response.status_code == 200
    assert response.json() == {"demo_read_only": True}
