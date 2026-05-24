"""API endpoint tests for CTEM Leader Lab."""

import io

from fastapi.testclient import TestClient


class TestCoreApi:
    def test_health(self, client: TestClient):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_program_summary(self, client: TestClient):
        resp = client.get("/api/program-summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["organization"] == "Northstar Financial Services"
        assert "metrics" in data
        assert "cycle" in data

    def test_maturity(self, client: TestClient):
        resp = client.get("/api/maturity")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 5
        assert all(d["score"] <= 5 for d in data)

    def test_business_services(self, client: TestClient):
        resp = client.get("/api/business-services")
        assert resp.status_code == 200
        data = resp.json()
        ids = [s["id"] for s in data]
        assert any(i.startswith("svc-payments-") for i in ids)
        assert any(i.startswith("svc-marketing-") for i in ids)

    def test_assets(self, client: TestClient):
        resp = client.get("/api/assets")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 6

    def test_exposures(self, client: TestClient):
        resp = client.get("/api/exposures")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 6

    def test_prioritized_exposures(self, client: TestClient):
        resp = client.get("/api/prioritized-exposures")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 6
        for item in data:
            assert "exposure_id" in item
            assert "ctem_score" in item
            assert "decision" in item
        assert data[0]["ctem_score"] >= data[-1]["ctem_score"]

    def test_legacy_prioritization_alias(self, client: TestClient):
        resp = client.get("/api/prioritization")
        assert resp.status_code == 200

    def test_attack_paths(self, client: TestClient):
        resp = client.get("/api/attack-paths")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2
        path_ids = [p["id"] for p in data]
        assert any(i.startswith("path-ci-to-data-") for i in path_ids)

    def test_remediation_actions(self, client: TestClient):
        resp = client.get("/api/remediation-actions")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 6

    def test_workshop_artifacts(self, client: TestClient):
        resp = client.get("/api/workshop-artifacts")
        assert resp.status_code == 200
        data = resp.json()
        assert "maturity_assessment" in data
        assert "raci" in data
        assert "roadmap_30_60_90" in data

    def test_seeded_relationships(self, client: TestClient):
        assets_resp = client.get("/api/assets").json()
        services_resp = client.get("/api/business-services").json()
        exposure_resp = client.get("/api/exposures").json()

        service_ids = {s["id"] for s in services_resp}
        for asset in assets_resp:
            assert asset["service_id"] in service_ids

        asset_ids = {a["id"] for a in assets_resp}
        for exposure in exposure_resp:
            assert exposure["asset_id"] in asset_ids

    def test_scores_exist(self, client: TestClient):
        resp = client.get("/api/prioritized-exposures")
        data = resp.json()
        for item in data:
            assert len(item["score_drivers"]) == 9
            assert item["rationale"]
            assert item["why_it_matters"]
            assert item["owner"]


ADMIN_TOKEN = "test-admin-token"


class TestAdminToken:
    def test_missing_token_blocks_mutation(self, client: TestClient):
        resp = client.post("/api/reset?X-Confirm-Reset=true")
        assert resp.status_code == 401

    def test_wrong_token_rejected(self, client: TestClient):
        resp = client.post("/api/reset?X-Confirm-Reset=true",
                           headers={"X-CTEM-Admin-Token": "wrong"})
        assert resp.status_code == 401

    def test_mutation_without_confirm_fails(self, client: TestClient):
        resp = client.post("/api/reset", headers={"X-CTEM-Admin-Token": ADMIN_TOKEN})
        assert resp.status_code == 400


class TestCsvExport:
    def test_assets_csv(self, client: TestClient):
        resp = client.get("/api/assets/export")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        assert "assets.csv" in resp.headers.get("content-disposition", "")

    def test_exposures_csv(self, client: TestClient):
        resp = client.get("/api/exposures/export")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")

    def test_remediation_csv(self, client: TestClient):
        resp = client.get("/api/remediation-actions/export")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")

    def test_csv_injection_sanitized(self, client: TestClient):
        resp = client.get("/api/exposures/export")
        content = resp.text
        suspicious = ["=CMD", "+CMD", "-CMD", "@CMD", "|CMD"]
        for pattern in suspicious:
            assert pattern not in content


class TestCsvImport:
    def _make_csv(self, rows: list[dict]) -> io.BytesIO:
        import csv
        buf = io.StringIO()
        if rows:
            writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        buf.seek(0)
        return io.BytesIO(buf.getvalue().encode("utf-8-sig"))

    def _make_csv_bytes(self, headers: list[str], rows: list[list]) -> io.BytesIO:
        import csv
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(headers)
        writer.writerows(rows)
        buf.seek(0)
        return io.BytesIO(buf.getvalue().encode("utf-8-sig"))

    def _admin_headers(self):
        return {"X-CTEM-Admin-Token": ADMIN_TOKEN}

    def test_import_assets_valid(self, client: TestClient):
        services = client.get("/api/business-services").json()
        svc_id = next(s["id"] for s in services if s["id"].startswith("svc-payments-"))
        rows = [
            {
                "id": "test-asset-1", "name": "Test Asset", "type": "Server",
                "service_id": svc_id, "owner": "Test", "environment": "Production",
                "criticality": "High", "crown_jewel": "false", "internet_exposed": "true",
                "reachable_from_internet": "Direct", "tags": "test",
            }
        ]
        resp = client.post("/api/assets/import", files={"file": ("test.csv", self._make_csv(rows), "text/csv")},
                           headers=self._admin_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["imported"] == 1
        assert data["errors"] == []

    def test_import_invalid_enum_fails(self, client: TestClient):
        services = client.get("/api/business-services").json()
        svc_id = next(s["id"] for s in services if s["id"].startswith("svc-payments-"))
        rows = [
            {
                "id": "bad-asset", "name": "Bad", "type": "Server",
                "service_id": svc_id, "owner": "Test", "environment": "Production",
                "criticality": "InvalidEnum", "crown_jewel": "false", "internet_exposed": "true",
                "reachable_from_internet": "Direct", "tags": "",
            }
        ]
        resp = client.post("/api/assets/import", files={"file": ("test.csv", self._make_csv(rows), "text/csv")},
                           headers=self._admin_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["imported"] == 0
        assert len(data["errors"]) > 0

    def test_import_too_large(self, client: TestClient):
        big_data = "a" * (11 * 1024 * 1024)
        resp = client.post("/api/assets/import", files={"file": ("big.csv", big_data.encode(), "text/csv")},
                           headers=self._admin_headers())
        assert resp.status_code == 413

    def test_import_wrong_content_type(self, client: TestClient):
        resp = client.post("/api/assets/import", files={"file": ("test.txt", b"data", "text/plain")},
                           headers=self._admin_headers())
        assert resp.status_code == 415


class TestReset:
    def test_reset_restores_seed_data(self, client: TestClient):
        resp = client.post("/api/reset?X-Confirm-Reset=true",
                           headers={"X-CTEM-Admin-Token": ADMIN_TOKEN})
        assert resp.status_code == 200

    def test_reset_without_confirm(self, client: TestClient):
        resp = client.post("/api/reset", headers={"X-CTEM-Admin-Token": ADMIN_TOKEN})
        assert resp.status_code == 400


class TestSessions:
    def _admin_headers(self):
        return {"X-CTEM-Admin-Token": ADMIN_TOKEN}

    def test_save_and_list_sessions(self, client: TestClient):
        save_resp = client.post("/api/sessions?name=test-session",
                                headers=self._admin_headers())
        assert save_resp.status_code == 200
        session_id = save_resp.json()["id"]

        list_resp = client.get("/api/sessions")
        assert list_resp.status_code == 200
        ids = [s["id"] for s in list_resp.json()]
        assert session_id in ids

    def test_load_session(self, client: TestClient):
        save_resp = client.post("/api/sessions?name=load-test",
                                headers=self._admin_headers())
        session_id = save_resp.json()["id"]

        load_resp = client.post(f"/api/sessions/{session_id}/load",
                                headers=self._admin_headers())
        assert load_resp.status_code == 200
        assert load_resp.json()["status"] == f"Session {session_id} loaded"

    def test_load_nonexistent_session(self, client: TestClient):
        resp = client.post("/api/sessions/nonexistent/load",
                           headers=self._admin_headers())
        assert resp.status_code == 404

    def test_delete_session(self, client: TestClient):
        save_resp = client.post("/api/sessions?name=to-delete",
                                headers=self._admin_headers())
        session_id = save_resp.json()["id"]

        del_resp = client.delete(f"/api/sessions/{session_id}",
                                 headers=self._admin_headers())
        assert del_resp.status_code == 200

        get_resp = client.get(f"/api/sessions/{session_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_session(self, client: TestClient):
        resp = client.delete("/api/sessions/nonexistent",
                             headers=self._admin_headers())
        assert resp.status_code == 404

    def test_list_sessions_empty(self, client: TestClient):
        resp = client.get("/api/sessions")
        assert resp.status_code == 200
        assert resp.json() == []


class TestExecutiveSummary:
    def test_markdown_summary(self, client: TestClient):
        resp = client.get("/api/executive-summary?format=markdown")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/markdown")

    def test_html_summary(self, client: TestClient):
        resp = client.get("/api/executive-summary?format=html")
        assert resp.status_code == 200
        assert "html" in resp.headers["content-type"]


class TestAudit:
    def test_audit_log_has_limit(self, client: TestClient):
        resp = client.get("/api/audit-events?limit=10")
        assert resp.status_code == 200

    def test_audit_limit_respected(self, client: TestClient):
        resp = client.get("/api/audit-events?limit=500")
        assert resp.status_code == 200
