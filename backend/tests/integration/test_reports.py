"""Integration tests for reports endpoints."""

import pytest


@pytest.mark.asyncio
async def test_spending_report(client, auth_headers):
    response = await client.get(
        "/api/v1/reports/spending",
        params={"from_date": "2024-01-01", "to_date": "2024-01-31"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "categories" in data
    assert "from_date" in data


@pytest.mark.asyncio
async def test_income_vs_expenses(client, auth_headers):
    response = await client.get(
        "/api/v1/reports/income-vs-expenses",
        params={"from_date": "2024-01-01", "to_date": "2024-03-31"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "periods" in data
    assert "total_income" in data
    assert "total_expenses" in data


@pytest.mark.asyncio
async def test_net_worth(client, auth_headers):
    response = await client.get("/api/v1/reports/net-worth", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "net_worth" in data
    assert "accounts" in data
    assert "total_assets" in data


@pytest.mark.asyncio
async def test_trends_report(client, auth_headers):
    response = await client.get(
        "/api/v1/reports/trends",
        params={"months": 6},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "trends" in data
    assert data["months"] == 6
