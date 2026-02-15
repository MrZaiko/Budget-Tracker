"""Extended integration tests for accounts — update, delete, conflict guard."""

import pytest


@pytest.mark.asyncio
async def test_update_account(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Old Acc", "type": "checking", "currency": "USD"},
        headers=auth_headers,
    )
    acc_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/accounts/{acc_id}",
        json={"name": "New Acc", "is_active": False},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["name"] == "New Acc"
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_delete_account_success(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "DeletableAcc", "type": "cash", "currency": "USD"},
        headers=auth_headers,
    )
    acc_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/accounts/{acc_id}", headers=auth_headers)
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_account_with_transaction_returns_409(client, auth_headers):
    """Cannot delete an account that has linked transactions."""
    # Create account
    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Locked Acc", "type": "checking", "currency": "USD"},
        headers=auth_headers,
    )
    acc_id = acc_resp.json()["id"]

    # Create a transaction on it
    from datetime import date
    tx_resp = await client.post(
        "/api/v1/transactions",
        json={
            "account_id": acc_id,
            "type": "expense",
            "amount": "10.00",
            "currency": "USD",
            "date": str(date.today()),
        },
        headers=auth_headers,
    )
    assert tx_resp.status_code == 201

    # Now try to delete the account
    del_resp = await client.delete(f"/api/v1/accounts/{acc_id}", headers=auth_headers)
    assert del_resp.status_code == 409
    assert del_resp.json()["code"] == "account_has_transactions"


@pytest.mark.asyncio
async def test_update_account_not_found(client, auth_headers):
    import uuid
    response = await client.patch(
        f"/api/v1/accounts/{uuid.uuid4()}",
        json={"name": "Ghost"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_account_balance_reflects_transactions(client, auth_headers):
    """Account balance should include initial_balance + transactions."""
    from datetime import date

    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Balance Acc", "type": "checking", "currency": "USD", "initial_balance": "1000.00"},
        headers=auth_headers,
    )
    acc_id = acc_resp.json()["id"]

    # Add income
    await client.post(
        "/api/v1/transactions",
        json={"account_id": acc_id, "type": "income", "amount": "500.00", "currency": "USD", "date": str(date.today())},
        headers=auth_headers,
    )
    # Add expense
    await client.post(
        "/api/v1/transactions",
        json={"account_id": acc_id, "type": "expense", "amount": "200.00", "currency": "USD", "date": str(date.today())},
        headers=auth_headers,
    )

    get_resp = await client.get(f"/api/v1/accounts/{acc_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    balance = float(get_resp.json()["balance"])
    assert balance == pytest.approx(1300.0)
