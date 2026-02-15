"""Integration tests for currencies endpoints."""

import pytest


@pytest.mark.asyncio
async def test_list_currencies(client, auth_headers):
    response = await client.get("/api/v1/currencies", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # May be empty in test db (no seed run), which is still valid


@pytest.mark.asyncio
async def test_get_latest_rates(client, auth_headers):
    response = await client.get("/api/v1/currencies/rates", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "base" in data
    assert "rates" in data
    assert "date" in data


@pytest.mark.asyncio
async def test_get_latest_rates_custom_base(client, auth_headers):
    response = await client.get(
        "/api/v1/currencies/rates",
        params={"base": "EUR"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["base"] == "EUR"


@pytest.mark.asyncio
async def test_get_historical_rates(client, auth_headers):
    response = await client.get(
        "/api/v1/currencies/rates/history",
        params={"from_date": "2024-01-01", "to_date": "2024-01-31"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "base" in data
    assert "rates" in data
