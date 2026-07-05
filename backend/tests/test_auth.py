"""
Authentication endpoint tests for TaskFlow API.

Tests: POST /auth/v1/signup
       POST /auth/v1/login
       POST /auth/v1/refresh
       POST /auth/v1/logout
       GET  /auth/v1/me
"""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------
class TestSignup:
    async def test_signup_success(self, client: AsyncClient):
        payload = {
            "name": "Alice",
            "email": "alice@example.com",
            "password": "password123",
        }
        resp = await client.post("/auth/v1/signup", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "alice@example.com"
        assert data["name"] == "Alice"
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert "id" in data
        assert "hashed_password" not in data

    async def test_signup_duplicate_email(self, client: AsyncClient, registered_user):
        payload = {
            "name": "Duplicate",
            "email": "test@example.com",  # same as registered_user
            "password": "anything",
        }
        resp = await client.post("/auth/v1/signup", json=payload)
        assert resp.status_code == 409

    async def test_signup_invalid_email(self, client: AsyncClient):
        payload = {"name": "Bad", "email": "not-an-email", "password": "pass"}
        resp = await client.post("/auth/v1/signup", json=payload)
        assert resp.status_code == 422

    async def test_signup_missing_fields(self, client: AsyncClient):
        resp = await client.post("/auth/v1/signup", json={"name": "Incomplete"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
class TestLogin:
    async def test_login_success(self, client: AsyncClient, registered_user):
        resp = await client.post(
            "/auth/v1/login",
            data={"username": "test@example.com", "password": "secret123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, registered_user):
        resp = await client.post(
            "/auth/v1/login",
            data={"username": "test@example.com", "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        resp = await client.post(
            "/auth/v1/login",
            data={"username": "nobody@example.com", "password": "pass"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Me
# ---------------------------------------------------------------------------
class TestMe:
    async def test_get_me_success(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/auth/v1/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"
        assert "id" in data

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/auth/v1/me")
        assert resp.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        resp = await client.get(
            "/auth/v1/me", headers={"Authorization": "Bearer invalidtoken"}
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------
class TestRefresh:
    async def test_refresh_success(self, client: AsyncClient, auth_tokens: dict):
        resp = await client.post(
            "/auth/v1/refresh",
            json={"refresh_token": auth_tokens["refresh_token"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_with_access_token_fails(
        self, client: AsyncClient, auth_tokens: dict
    ):
        """Access tokens must not be accepted as refresh tokens."""
        resp = await client.post(
            "/auth/v1/refresh",
            json={"refresh_token": auth_tokens["access_token"]},
        )
        assert resp.status_code == 401

    async def test_refresh_invalid_token(self, client: AsyncClient):
        resp = await client.post(
            "/auth/v1/refresh", json={"refresh_token": "garbage.token.here"}
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------
class TestLogout:
    async def test_logout_success(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/auth/v1/logout", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Successfully logged out"
