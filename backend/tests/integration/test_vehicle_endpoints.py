from fastapi.testclient import TestClient


def test_vehicle_endpoints_create_read_update_and_delete(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/vehicles",
        json={
            "brand": " Honda ",
            "model": " Civic ",
            "year": 2022,
            "license_plate": " ga 1234 ",
            "current_mileage": 15000,
        },
    )

    assert create_response.status_code == 201
    created_vehicle = create_response.json()
    assert created_vehicle["brand"] == "Honda"
    assert created_vehicle["license_plate"] == "GA 1234"

    vehicle_id = created_vehicle["id"]
    list_response = client.get("/api/v1/vehicles")
    detail_response = client.get(f"/api/v1/vehicles/{vehicle_id}")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert detail_response.status_code == 200
    assert detail_response.json() == created_vehicle

    update_response = client.put(
        f"/api/v1/vehicles/{vehicle_id}",
        json={
            "brand": "Honda",
            "model": "Civic Sport",
            "year": 2022,
            "license_plate": "GA 1234",
            "current_mileage": 17500,
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["model"] == "Civic Sport"
    assert update_response.json()["current_mileage"] == 17500

    delete_response = client.delete(f"/api/v1/vehicles/{vehicle_id}")

    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/vehicles/{vehicle_id}").status_code == 404


def test_duplicate_license_plate_returns_conflict(client: TestClient) -> None:
    first_response = client.post(
        "/api/v1/vehicles",
        json={
            "brand": "Honda",
            "model": "Civic",
            "year": 2022,
            "license_plate": "GA 1234",
            "current_mileage": 1000,
        },
    )
    second_response = client.post(
        "/api/v1/vehicles",
        json={
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2021,
            "license_plate": "GA 1234",
            "current_mileage": 2000,
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_vehicle_with_maintenance_cannot_be_deleted(
    client: TestClient, vehicle_id: int
) -> None:
    maintenance_response = client.post(
        f"/api/v1/vehicles/{vehicle_id}/maintenance",
        json={
            "maintenance_type": "Oil change",
            "maintenance_date": "2026-01-15",
            "mileage": 15000,
            "cost": "89.95",
        },
    )

    assert maintenance_response.status_code == 201

    delete_response = client.delete(f"/api/v1/vehicles/{vehicle_id}")

    assert delete_response.status_code == 409
    assert client.get(f"/api/v1/vehicles/{vehicle_id}").status_code == 200


def test_missing_vehicle_returns_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/vehicles/999999")

    assert response.status_code == 404
