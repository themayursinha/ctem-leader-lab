from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_core_api_responses_are_json_serializable():
    for path in [
        "/api/program-summary",
        "/api/maturity",
        "/api/business-services",
        "/api/assets",
        "/api/exposures",
        "/api/prioritized-exposures",
        "/api/attack-paths",
        "/api/remediation-actions",
        "/api/workshop-artifacts",
    ]:
        response = client.get(path)
        assert response.status_code == 200
        assert response.json()


def test_seeded_relationships_are_linked():
    assets = {asset["id"] for asset in client.get("/api/assets").json()}
    services = {service["id"] for service in client.get("/api/business-services").json()}
    exposures = client.get("/api/exposures").json()
    paths = client.get("/api/attack-paths").json()
    actions = client.get("/api/remediation-actions").json()

    assert all(exposure["asset_id"] in assets for exposure in exposures)
    assert all(step["asset_id"] in assets for path in paths for step in path["steps"])
    assert all(path["business_service_id"] in services for path in paths)
    assert all(action["exposure_id"] in {exposure["id"] for exposure in exposures} for action in actions)
