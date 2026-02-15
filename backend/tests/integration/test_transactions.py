"""Integration tests for transactions endpoints."""

import pytest


@pytest.mark.asyncio
async def test_list_transactions_returns_paginated(client, auth_headers):
    response = await client.get("/api/v1/transactions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_transaction_not_found(client, auth_headers):
    import uuid
    response = await client.get(f"/api/v1/transactions/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_transfer_requires_to_account(client, auth_headers):
    """Creating a transfer without transfer_to_account_id should return 400."""
    import uuid

    payload = {
        "account_id": str(uuid.uuid4()),
        "type": "transfer",
        "amount": "100.00",
        "currency": "USD",
        "date": "2024-01-15",
    }
    response = await client.post("/api/v1/transactions", json=payload, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "transfer_account_required"
