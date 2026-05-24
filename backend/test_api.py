import csv
import io
import os

os.environ["CTEM_DB_PATH"] = "/tmp/ctem_test.db"

from fastapi.testclient import TestClient

from data import DATA
from main import app


client = TestClient(app)


# ---------- CSV helpers ----------

def _asset_csv_row(**overrides):
    fields = {
        "id": "test-asset-1", "name": "Test Asset", "type": "Web Application",
        "service_id": "svc-payments", "owner": "Test Team", "environment": "Production",
        "criticality": "Critical", "crown_jewel": "True", "internet_exposed": "True",
        "reachable_from_internet": "Direct", "tags": "test;demo",
    }
    fields.update(overrides)
    return fields


def _exposure_csv_row(**overrides):
    fields = {
        "id": "test-exp-1", "title": "Test Exposure", "description": "A test exposure",
        "exposure_type": "CVE", "asset_id": "asset-payment-api", "severity": "Critical",
        "cvss": "9.0", "epss_probability": "0.5", "kev_signal": "True",
        "ransomware_observed": "False", "identity_risk": "2", "control_gap": "3",
        "attack_path_proximity": "Crown Jewel", "remediation_effort": "Medium",
        "evidence_confidence": "High", "evidence": "Test evidence",
        "suggested_action": "Test action",
    }
    fields.update(overrides)
    return fields


def _remediation_csv_row(**overrides):
    fields = {
        "id": "test-act-1", "exposure_id": "test-exp-1",
        "title": "Test remediation", "owner": "Test Team", "team": "Test",
        "status": "To Do", "priority": "Act", "sla": "7 days",
        "due_in_days": "5", "playbook": "Test playbook", "dependency": "None",
        "retest_status": "Not Started", "risk_acceptance_required": "False",
    }
    fields.update(overrides)
    return fields


def _make_csv(rows: list[dict]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


# ---------- Existing tests ----------


def test_core_api_responses_are_json_serializable():
    DATA.reset()
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
    DATA.reset()
    assets = {asset["id"] for asset in client.get("/api/assets").json()}
    services = {service["id"] for service in client.get("/api/business-services").json()}
    exposures = client.get("/api/exposures").json()
    paths = client.get("/api/attack-paths").json()
    actions = client.get("/api/remediation-actions").json()

    assert all(exposure["asset_id"] in assets for exposure in exposures)
    assert all(step["asset_id"] in assets for path in paths for step in path["steps"])
    assert all(path["business_service_id"] in services for path in paths)
    assert all(action["exposure_id"] in {exposure["id"] for exposure in exposures} for action in actions)


# ---------- CSV export tests ----------


def test_assets_export_returns_valid_csv():
    resp = client.get("/api/assets/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "assets.csv" in resp.headers["content-disposition"]

    reader = csv.DictReader(io.StringIO(resp.text))
    rows = list(reader)
    assert len(rows) >= 1
    first = rows[0]
    assert "id" in first
    assert "name" in first


def test_exposures_export_returns_valid_csv():
    resp = client.get("/api/exposures/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    reader = csv.DictReader(io.StringIO(resp.text))
    rows = list(reader)
    assert len(rows) >= 1
    assert "id" in rows[0]


def test_remediation_export_returns_valid_csv():
    resp = client.get("/api/remediation-actions/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    reader = csv.DictReader(io.StringIO(resp.text))
    rows = list(reader)
    assert len(rows) >= 1
    assert "id" in rows[0]


def test_csv_export_sanitizes_injection():
    DATA.reset()
    assert client.get("/api/assets/export").status_code == 200


# ---------- CSV import tests ----------


def test_assets_import_succeeds():
    DATA.reset()
    csv_bytes = _make_csv([_asset_csv_row()])
    resp = client.post("/api/assets/import", files={"file": ("test.csv", csv_bytes, "text/csv")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == 1
    assert data["errors"] == []

    assets = client.get("/api/assets").json()
    ids = {a["id"] for a in assets}
    assert "test-asset-1" in ids


def test_exposures_import_succeeds():
    DATA.reset()
    csv_bytes = _make_csv([_exposure_csv_row()])
    resp = client.post("/api/exposures/import", files={"file": ("test.csv", csv_bytes, "text/csv")})
    assert resp.status_code == 200
    assert resp.json()["imported"] == 1

    exposures = client.get("/api/exposures").json()
    ids = {e["id"] for e in exposures}
    assert "test-exp-1" in ids


def test_remediation_import_succeeds():
    DATA.reset()
    csv_bytes = _make_csv([_remediation_csv_row()])
    resp = client.post("/api/remediation-actions/import", files={"file": ("test.csv", csv_bytes, "text/csv")})
    assert resp.status_code == 200
    assert resp.json()["imported"] == 1


def test_import_rejects_invalid_enum():
    DATA.reset()
    csv_bytes = _make_csv([_asset_csv_row(criticality="InvalidEnum")])
    resp = client.post("/api/assets/import", files={"file": ("test.csv", csv_bytes, "text/csv")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == 0
    assert len(data["errors"]) >= 1


def test_import_rejects_missing_required_fields():
    DATA.reset()
    csv_bytes = _make_csv([_asset_csv_row(id="")])
    resp = client.post("/api/assets/import", files={"file": ("test.csv", csv_bytes, "text/csv")})
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == 0
    assert len(data["errors"]) >= 1


def test_import_rejects_file_too_large():
    DATA.reset()
    big = (_asset_csv_row(id=str(i)) for i in range(15_000))
    csv_bytes = _make_csv(list(big))
    resp = client.post("/api/assets/import", files={"file": ("big.csv", csv_bytes, "text/csv")})
    assert resp.status_code == 422


def test_import_rejects_wrong_content_type():
    DATA.reset()
    csv_bytes = _make_csv([_asset_csv_row()])
    resp = client.post("/api/assets/import", files={"file": ("test.exe", csv_bytes, "application/x-msdownload")})
    assert resp.status_code == 415


# ---------- Reset test ----------


def test_reset_requires_confirmation():
    DATA.reset()
    resp = client.post("/api/reset")
    assert resp.status_code == 400


def test_reset_restores_seed_data():
    DATA.reset()
    csv_bytes = _make_csv([_asset_csv_row(id="temp-imported")])
    client.post("/api/assets/import", files={"file": ("test.csv", csv_bytes, "text/csv")})
    assert "temp-imported" in {a["id"] for a in client.get("/api/assets").json()}

    resp = client.post("/api/reset?X-Confirm-Reset=true")
    assert resp.status_code == 200

    assets = client.get("/api/assets").json()
    ids = {a["id"] for a in assets}
    assert "temp-imported" not in ids
    assert "asset-payment-api" in ids


# ---------- Session tests ----------


def test_save_and_list_sessions():
    DATA.reset()
    resp = client.post("/api/sessions?name=Test%20Session%201")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["name"] == "Test Session 1"
    session_id = data["id"]

    sessions = client.get("/api/sessions").json()
    ids = [s["id"] for s in sessions]
    assert session_id in ids


def test_get_session():
    DATA.reset()
    resp = client.post("/api/sessions?name=MySession")
    session_id = resp.json()["id"]

    resp = client.get(f"/api/sessions/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "MySession"


def test_get_session_not_found():
    resp = client.get("/api/sessions/nonexistent-id")
    assert resp.status_code == 404


def test_load_session():
    DATA.reset()
    exposures_before = client.get("/api/exposures").json()
    before_ids = {e["id"] for e in exposures_before}

    resp = client.post("/api/sessions?name=Snapshot")
    session_id = resp.json()["id"]

    DATA.reset()
    exposures_after_reset = client.get("/api/exposures").json()
    assert {e["id"] for e in exposures_after_reset} == before_ids

    resp = client.post(f"/api/sessions/{session_id}/load")
    assert resp.status_code == 200

    exposures_loaded = client.get("/api/exposures").json()
    assert {e["id"] for e in exposures_loaded} == before_ids


def test_delete_session():
    DATA.reset()
    resp = client.post("/api/sessions?name=DeleteMe")
    session_id = resp.json()["id"]

    resp = client.delete(f"/api/sessions/{session_id}")
    assert resp.status_code == 200

    resp = client.get(f"/api/sessions/{session_id}")
    assert resp.status_code == 404


def test_delete_session_not_found():
    resp = client.delete("/api/sessions/nonexistent")
    assert resp.status_code == 404


# ---------- Executive summary tests ----------


def test_executive_summary_markdown():
    DATA.reset()
    resp = client.get("/api/executive-summary?format=markdown")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/markdown")
    body = resp.text
    assert "CTEM Executive Summary" in body
    assert "Act Decisions" in body
    assert "Northstar Financial Services" in body


def test_executive_summary_html():
    DATA.reset()
    resp = client.get("/api/executive-summary?format=html")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert "<h2>" in resp.text or "CTEM Executive Summary" in resp.text


def test_executive_summary_defaults_to_markdown():
    DATA.reset()
    resp = client.get("/api/executive-summary")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/markdown")


# ---------- Health, provenance, admin token, and audit tests ----------


def test_health_endpoint():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_seeded_exposures_include_provenance():
    DATA.reset()
    exposure = client.get("/api/exposures").json()[0]
    assert exposure["source"]
    assert exposure["source_reference"]
    assert exposure["last_seen"]
    assert exposure["validated_at"]


def test_exposure_csv_export_includes_provenance_fields():
    DATA.reset()
    resp = client.get("/api/exposures/export")
    reader = csv.DictReader(io.StringIO(resp.text))
    assert "source" in reader.fieldnames
    assert "validated_at" in reader.fieldnames


def test_optional_provenance_fields_do_not_break_legacy_import():
    DATA.reset()
    row = _exposure_csv_row()
    for key in ["source", "source_reference", "first_seen", "last_seen", "validated_at", "evidence_owner", "evidence_expires_at"]:
        row.pop(key, None)
    csv_bytes = _make_csv([row])
    resp = client.post("/api/exposures/import", files={"file": ("legacy.csv", csv_bytes, "text/csv")})
    assert resp.status_code == 200
    assert resp.json()["imported"] == 1


def test_admin_token_blocks_mutation_when_configured(monkeypatch):
    DATA.reset()
    monkeypatch.setenv("CTEM_ADMIN_TOKEN", "test-token")
    csv_bytes = _make_csv([_asset_csv_row(id="blocked-asset")])

    missing = client.post("/api/assets/import", files={"file": ("test.csv", csv_bytes, "text/csv")})
    assert missing.status_code == 401

    wrong = client.post(
        "/api/assets/import",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
        headers={"X-CTEM-Admin-Token": "wrong"},
    )
    assert wrong.status_code == 401

    ok = client.post(
        "/api/assets/import",
        files={"file": ("test.csv", csv_bytes, "text/csv")},
        headers={"X-CTEM-Admin-Token": "test-token"},
    )
    assert ok.status_code == 200
    assert ok.json()["imported"] == 1


def test_audit_events_are_recorded_for_mutations():
    DATA.reset()
    csv_bytes = _make_csv([_asset_csv_row(id="audit-asset")])
    resp = client.post("/api/assets/import", files={"file": ("test.csv", csv_bytes, "text/csv")})
    assert resp.status_code == 200

    events = client.get("/api/audit-events?limit=10").json()
    assert events[0]["action"] == "import_assets"
    assert events[0]["resource_type"] == "assets"
    assert events[0]["metadata"]["row_count"] == 1


def test_audit_events_limit_is_respected():
    DATA.record_audit_event("test_event_one", "test", None, "one", {})
    DATA.record_audit_event("test_event_two", "test", None, "two", {})
    resp = client.get("/api/audit-events?limit=1")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
