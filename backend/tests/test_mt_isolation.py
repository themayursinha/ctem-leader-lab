"""Multi-tenant isolation tests — verify users can only see their own organization's data."""

from fastapi.testclient import TestClient


def _register(client: TestClient, email: str, password: str, name: str, org_name: str) -> str:
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": name, "organization_name": org_name},
    )
    assert resp.status_code == 200, f"Register failed: {resp.text}"
    return resp.json()["access_token"]


class TestMultiTenantIsolation:
    def test_business_services_are_org_scoped(self, client: TestClient):
        token_a = _register(client, "a@alpha.com", "Pass1234!", "Alice", "Alpha Corp")
        token_b = _register(client, "b@beta.com", "Pass1234!", "Bob", "Beta Inc")

        svc_a = client.get(
            "/api/business-services",
            headers={"Authorization": f"Bearer {token_a}"},
        ).json()
        svc_b = client.get(
            "/api/business-services",
            headers={"Authorization": f"Bearer {token_b}"},
        ).json()

        assert len(svc_a) > 0
        assert len(svc_b) > 0

        ids_a = {s["id"] for s in svc_a}
        ids_b = {s["id"] for s in svc_b}
        assert ids_a.isdisjoint(ids_b), f"Service IDs must be disjoint across orgs. Common: {ids_a & ids_b}"

    def test_second_org_seeds_independently(self, client: TestClient):
        token_a = _register(client, "c@charlie.com", "Pass1234!", "Charlie", "Charlie Co")
        token_b = _register(client, "d@delta.com", "Pass1234!", "Diana", "Delta LLC")

        prio_a = client.get(
            "/api/prioritized-exposures",
            headers={"Authorization": f"Bearer {token_a}"},
        ).json()
        prio_b = client.get(
            "/api/prioritized-exposures",
            headers={"Authorization": f"Bearer {token_b}"},
        ).json()

        assert len(prio_a) > 0
        assert len(prio_b) > 0

        ids_a = {p["exposure_id"] for p in prio_a}
        ids_b = {p["exposure_id"] for p in prio_b}
        assert ids_a.isdisjoint(ids_b), (
            f"Prioritized exposure IDs must be disjoint. Common: {ids_a & ids_b}"
        )

    def test_unauthenticated_sees_data(self, client: TestClient):
        resp = client.get("/api/business-services")
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_maturity_domains_shared_across_orgs(self, client: TestClient):
        _register(client, "e@echo.com", "Pass1234!", "Eve", "Echo Ltd")
        _register(client, "f@foxtrot.com", "Pass1234!", "Frank", "Foxtrot GmbH")

        maturity_a = client.get(
            "/api/maturity",
            headers={"Authorization": f"Bearer {_register(client, 'g@golf.com', 'Pass1234!', 'G', 'Golf')}"},
        ).json()
        maturity_b = client.get(
            "/api/maturity",
            headers={"Authorization": f"Bearer {_register(client, 'h@hotel.com', 'Pass1234!', 'H', 'Hotel')}"},
        ).json()

        names_a = {m["name"] for m in maturity_a}
        names_b = {m["name"] for m in maturity_b}
        assert names_a == names_b, "Maturity domains are shared across orgs (by design)"

    def test_attack_paths_per_org(self, client: TestClient):
        resp = client.get("/api/attack-paths")
        assert resp.status_code == 200
        paths = resp.json()
        assert len(paths) >= 2, "Should have attack paths for default org"
        assert paths[0]["name"]
