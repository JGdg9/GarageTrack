from decimal import Decimal

from fastapi.testclient import TestClient


def test_maintenance_endpoints_create_read_update_and_delete(
    client: TestClient, vehicle_id: int
) -> None:
    create_response = client.post(
        f"/api/v1/vehicles/{vehicle_id}/maintenance",
        json={
            "maintenance_type": " Oil change ",
            "maintenance_date": "2026-01-15",
            "mileage": 15000,
            "cost": "125.50",
            "description": "  Synthetic oil  ",
        },
    )

    assert create_response.status_code == 201
    created_record = create_response.json()
    assert created_record["maintenance_type"] == "Oil change"
    assert created_record["description"] == "Synthetic oil"
    assert Decimal(str(created_record["cost"])) == Decimal("125.50")

    maintenance_id = created_record["id"]
    history_response = client.get(f"/api/v1/vehicles/{vehicle_id}/maintenance")

    assert history_response.status_code == 200
    assert history_response.json() == [created_record]

    update_response = client.put(
        f"/api/v1/maintenance/{maintenance_id}",
        json={
            "maintenance_type": "Brake service",
            "maintenance_date": "2026-02-10",
            "mileage": 16000,
            "cost": "48.25",
            "description": "Front pads",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["maintenance_type"] == "Brake service"

    expense_response = client.get(f"/api/v1/vehicles/{vehicle_id}/expenses")

    assert expense_response.status_code == 200
    assert Decimal(str(expense_response.json()["total_expenses"])) == Decimal("48.25")

    delete_response = client.delete(f"/api/v1/maintenance/{maintenance_id}")

    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/vehicles/{vehicle_id}/maintenance").json() == []


def test_maintenance_cannot_reference_missing_vehicle(client: TestClient) -> None:
    response = client.post(
        "/api/v1/vehicles/999999/maintenance",
        json={
            "maintenance_type": "Oil change",
            "maintenance_date": "2026-01-15",
            "mileage": 15000,
            "cost": "89.95",
        },
    )

    assert response.status_code == 404


def test_statistics_include_vehicle_counts_and_expenses(
    client: TestClient, vehicle_id: int
) -> None:
    second_vehicle = client.post(
        "/api/v1/vehicles",
        json={
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2021,
            "current_mileage": 30000,
        },
    )
    maintenance = client.post(
        f"/api/v1/vehicles/{vehicle_id}/maintenance",
        json={
            "maintenance_type": "Oil change",
            "maintenance_date": "2026-01-15",
            "mileage": 15000,
            "cost": "89.95",
        },
    )

    assert second_vehicle.status_code == 201
    assert maintenance.status_code == 201

    statistics_response = client.get("/api/v1/statistics")
    statistics = statistics_response.json()

    assert statistics_response.status_code == 200
    assert statistics["total_vehicles"] == 2
    assert statistics["total_maintenance_records"] == 1
    assert Decimal(str(statistics["total_expenses"])) == Decimal("89.95")
    assert len(statistics["vehicle_expenses"]) == 2


def test_missing_maintenance_record_returns_not_found(client: TestClient) -> None:
    response = client.put(
        "/api/v1/maintenance/999999",
        json={
            "maintenance_type": "Oil change",
            "maintenance_date": "2026-01-15",
            "mileage": 15000,
            "cost": "89.95",
        },
    )

    assert response.status_code == 404
