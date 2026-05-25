"""Tests for authentication endpoints."""

from fastapi.testclient import TestClient


class TestAuthRegister:
    def test_register_creates_user(self, client: TestClient):
        resp = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "Test User",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["name"] == "Test User"

    def test_register_duplicate_email(self, client: TestClient):
        client.post("/api/auth/register", json={
            "email": "dup@example.com", "password": "pass", "name": "Dup",
        })
        resp = client.post("/api/auth/register", json={
            "email": "dup@example.com", "password": "pass", "name": "Dup",
        })
        assert resp.status_code == 409
        assert "already registered" in resp.json()["detail"]

    def test_register_rejects_passwords_over_bcrypt_limit(self, client: TestClient):
        resp = client.post("/api/auth/register", json={
            "email": "long@example.com",
            "password": "x" * 73,
            "name": "Long Password",
        })
        assert resp.status_code == 422


class TestAuthLogin:
    def test_login_success(self, client: TestClient):
        client.post("/api/auth/register", json={
            "email": "login@example.com", "password": "testpass", "name": "Login",
        })
        resp = client.post("/api/auth/login", json={
            "email": "login@example.com", "password": "testpass",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == "login@example.com"

    def test_login_wrong_password(self, client: TestClient):
        client.post("/api/auth/register", json={
            "email": "wrong@example.com", "password": "correct", "name": "Wrong",
        })
        resp = client.post("/api/auth/login", json={
            "email": "wrong@example.com", "password": "wrong",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        resp = client.post("/api/auth/login", json={
            "email": "nobody@example.com", "password": "pass",
        })
        assert resp.status_code == 401

    def test_login_rejects_passwords_over_bcrypt_limit(self, client: TestClient):
        resp = client.post("/api/auth/login", json={
            "email": "nobody@example.com", "password": "x" * 73,
        })
        assert resp.status_code == 422


class TestAuthMe:
    def test_me_returns_user(self, client: TestClient):
        reg = client.post("/api/auth/register", json={
            "email": "me@example.com", "password": "pass", "name": "Me",
        })
        token = reg.json()["access_token"]

        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "me@example.com"

    def test_me_no_token(self, client: TestClient):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_wrong_token(self, client: TestClient):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401
