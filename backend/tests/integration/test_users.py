"""Integration tests for users endpoints."""

import pytest


@pytest.mark.asyncio
async def test_get_me(client, auth_headers):
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"
    assert data["base_currency"] == "USD"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_update_me_display_name(client, auth_headers):
    response = await client.patch(
        "/api/v1/users/me",
        json={"display_name": "Updated Name"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_update_me_base_currency(client, auth_headers):
    response = await client.patch(
        "/api/v1/users/me",
        json={"base_currency": "EUR"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["base_currency"] == "EUR"


@pytest.mark.asyncio
async def test_update_me_no_fields(client, auth_headers):
    """Empty PATCH should return 200 with unchanged user."""
    response = await client.patch(
        "/api/v1/users/me",
        json={},
        headers=auth_headers,
    )
    assert response.status_code == 200
