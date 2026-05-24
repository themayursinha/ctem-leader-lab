"""Scoring engine tests for CTEM Leader Lab."""

from fastapi.testclient import TestClient

from app.core.scoring import decision_for_score


class TestScoringEngine:
    def test_medium_secret_outranks_isolated_high_cvss(self, client: TestClient):
        resp = client.get("/api/prioritized-exposures")
        data = resp.json()
        items = {item["exposure_id"]: item for item in data}
        secret = items.get("exp-ci-token")
        isolated_cve = items.get("exp-dev-wiki-cve")
        assert secret is not None
        assert isolated_cve is not None
        assert secret["ctem_score"] > isolated_cve["ctem_score"]

    def test_prioritized_exposure_has_rationale(self, client: TestClient):
        resp = client.get("/api/prioritized-exposures")
        data = resp.json()
        for item in data:
            assert item["rationale"]
            assert item["why_it_matters"]
            assert item["next_action"]
            assert item["owner"]
            assert item["sla"]

    def test_decision_thresholds(self):
        scores_and_decisions = [
            (80, "Act"),
            (75, "Act"),
            (74, "Attend"),
            (55, "Attend"),
            (54, "Monitor"),
            (35, "Monitor"),
            (34, "Track"),
            (0, "Track"),
        ]
        for score, expected in scores_and_decisions:
            assert decision_for_score(score) == expected, f"Score {score} should be {expected}"
