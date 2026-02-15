"""Integration tests for accounts endpoints."""

import pytest


@pytest.mark.asyncio
async def test_list_accounts_empty(client, auth_headers):
    response = await client.get("/api/v1/accounts", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_account(client, auth_headers):
    payload = {
        "name": "My Checking",
        "type": "checking",
        "currency": "USD",
        "initial_balance": "1000.00",
    }
    response = await client.post("/api/v1/accounts", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Checking"
    assert data["type"] == "checking"
    assert data["currency"] == "USD"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_account_not_found(client, auth_headers):
    import uuid
    response = await client.get(f"/api/v1/accounts/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == "not_found"


@pytest.mark.asyncio
async def test_create_and_get_account(client, auth_headers):
    payload = {
        "name": "Savings",
        "type": "savings",
        "currency": "EUR",
        "initial_balance": "5000.00",
    }
    create_resp = await client.post("/api/v1/accounts", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    account_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Savings"
