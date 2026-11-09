from fastapi.testclient import TestClient


def test_health_and_openapi_documentation_are_available(client: TestClient) -> None:
    health_response = client.get("/health")
    schema_response = client.get("/openapi.json")
    documentation_response = client.get("/docs")

    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}
    assert schema_response.status_code == 200
    assert "/api/v1/vehicles" in schema_response.json()["paths"]
    assert documentation_response.status_code == 200


def test_frontend_assets_are_served_by_fastapi(client: TestClient) -> None:
    page_response = client.get("/")
    script_response = client.get("/js/app.js")
    stylesheet_response = client.get("/styles.css")

    assert page_response.status_code == 200
    assert "<title>GarageTrack</title>" in page_response.text
    assert script_response.status_code == 200
    assert "createMaintenanceRecord" in script_response.text
    assert stylesheet_response.status_code == 200
    assert ".app-shell" in stylesheet_response.text
