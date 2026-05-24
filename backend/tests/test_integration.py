"""Integration tests that run against a real PostgreSQL database via Testcontainers.

These tests require Docker to be running. They are skipped if Docker is unavailable.
Run with: pytest tests/test_integration.py -v
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from app.dependencies import get_db
from app.main import create_app

pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION") == "1",
    reason="Integration tests skipped via SKIP_INTEGRATION=1",
)


@pytest.fixture(scope="module")
def postgres_container():
    """Start a PostgreSQL container and return its connection URL."""
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url()


@pytest.fixture(scope="module")
def db_session(postgres_container):
    """Create tables and return a session connected to the test PostgreSQL."""
    engine = create_engine(postgres_container, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="module")
def client(db_session):
    """FastAPI TestClient with PG-backed DB session."""
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestPostgresIntegration:
    """Smoke tests against a real PostgreSQL database."""

    def test_health(self, client):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_program_summary(self, client):
        resp = client.get("/api/program-summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "organization" in data
        assert "goal" in data
        assert "metrics" in data
        assert "cycle" in data
        assert len(data["metrics"]) > 0

    def test_business_services(self, client):
        resp = client.get("/api/business-services")
        assert resp.status_code == 200
        services = resp.json()
        assert len(services) > 0
        assert services[0]["name"]

    def test_assets(self, client):
        resp = client.get("/api/assets")
        assert resp.status_code == 200
        assets = resp.json()
        assert len(assets) > 0
        assert assets[0]["name"]

    def test_exposures(self, client):
        resp = client.get("/api/exposures")
        assert resp.status_code == 200
        exposures = resp.json()
        assert len(exposures) > 0
        assert exposures[0]["title"]

    def test_prioritized_exposures(self, client):
        resp = client.get("/api/prioritized-exposures")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        assert "ctem_score" in data[0]

    def test_attack_paths(self, client):
        resp = client.get("/api/attack-paths")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        assert data[0]["name"]

    def test_remediation_actions(self, client):
        resp = client.get("/api/remediation-actions")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        assert data[0]["title"]

    def test_csv_export_assets(self, client):
        resp = client.get("/api/assets/export")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/csv; charset=utf-8"
        assert b"id" in resp.content

    def test_csv_export_exposures(self, client):
        resp = client.get("/api/exposures/export")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/csv; charset=utf-8"
        assert b"id" in resp.content

    def test_maturity(self, client):
        resp = client.get("/api/maturity")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        assert data[0]["name"]
        assert 0 <= data[0]["score"] <= 5

    def test_workshop_artifacts(self, client):
        resp = client.get("/api/workshop-artifacts")
        assert resp.status_code == 200
        data = resp.json()
        assert "maturity_assessment" in data
        assert "raci" in data
        assert "roadmap_30_60_90" in data

    def test_admin_token_required(self, client):
        """Mutation without admin token should be rejected."""
        resp = client.post("/api/reset?X-Confirm-Reset=true")
        assert resp.status_code == 401
