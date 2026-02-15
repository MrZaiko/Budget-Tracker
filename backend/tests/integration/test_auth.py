"""Integration tests for auth endpoints."""

import pytest


@pytest.mark.asyncio
async def test_local_token_disabled(client):
    """Should return 403 when local auth is not enabled."""
    payload = {"email": "test@example.com", "password": "password123"}
    response = await client.post("/api/v1/auth/local/token", json=payload)
    assert response.status_code == 403
    data = response.json()
    assert data["code"] == "local_auth_disabled"


@pytest.mark.asyncio
async def test_get_me(client, auth_headers):
    """Should return current user info."""
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
