"""Extended integration tests for transactions — create, update, delete, filters."""

import uuid
from datetime import date

import pytest


@pytest.mark.asyncio
async def _create_account(client, auth_headers, name="Test Account"):
    resp = await client.post(
        "/api/v1/accounts",
        json={"name": name, "type": "checking", "currency": "USD"},
        headers=auth_headers,
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_income_transaction(client, auth_headers):
    acc_id = await _create_account(client, auth_headers, "Income Acc")
    payload = {
        "account_id": acc_id,
        "type": "income",
        "amount": "2500.00",
        "currency": "USD",
        "date": str(date.today()),
        "notes": "Salary",
    }
    response = await client.post("/api/v1/transactions", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "income"
    assert float(data["amount"]) == pytest.approx(2500.0)
    assert data["notes"] == "Salary"
    assert float(data["exchange_rate"]) == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_create_transfer_transaction(client, auth_headers):
    acc1 = await _create_account(client, auth_headers, "From Acc")
    acc2 = await _create_account(client, auth_headers, "To Acc")

    payload = {
        "account_id": acc1,
        "type": "transfer",
        "amount": "300.00",
        "currency": "USD",
        "date": str(date.today()),
        "transfer_to_account_id": acc2,
    }
    response = await client.post("/api/v1/transactions", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "transfer"
    assert data["transfer_to_account_id"] == acc2


@pytest.mark.asyncio
async def test_update_transaction(client, auth_headers):
    acc_id = await _create_account(client, auth_headers, "Update Acc")

    create_resp = await client.post(
        "/api/v1/transactions",
        json={"account_id": acc_id, "type": "expense", "amount": "50.00", "currency": "USD", "date": str(date.today())},
        headers=auth_headers,
    )
    tx_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/transactions/{tx_id}",
        json={"notes": "Updated note"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["notes"] == "Updated note"


@pytest.mark.asyncio
async def test_delete_transaction(client, auth_headers):
    acc_id = await _create_account(client, auth_headers, "Delete TX Acc")

    create_resp = await client.post(
        "/api/v1/transactions",
        json={"account_id": acc_id, "type": "expense", "amount": "25.00", "currency": "USD", "date": str(date.today())},
        headers=auth_headers,
    )
    tx_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_list_transactions_pagination(client, auth_headers):
    acc_id = await _create_account(client, auth_headers, "Paginate Acc")
    today = str(date.today())

    for i in range(5):
        await client.post(
            "/api/v1/transactions",
            json={"account_id": acc_id, "type": "expense", "amount": f"{10 + i}.00", "currency": "USD", "date": today},
            headers=auth_headers,
        )

    response = await client.get(
        "/api/v1/transactions",
        params={"page": 1, "page_size": 3, "account_id": acc_id},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 5
    assert len(data["items"]) <= 3
    assert data["page"] == 1
    assert data["pages"] >= 1


@pytest.mark.asyncio
async def test_filter_transactions_by_type(client, auth_headers):
    acc_id = await _create_account(client, auth_headers, "Filter Acc")
    today = str(date.today())

    await client.post(
        "/api/v1/transactions",
        json={"account_id": acc_id, "type": "income", "amount": "100.00", "currency": "USD", "date": today},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/transactions",
        json={"account_id": acc_id, "type": "expense", "amount": "50.00", "currency": "USD", "date": today},
        headers=auth_headers,
    )

    response = await client.get(
        "/api/v1/transactions",
        params={"type": "income", "account_id": acc_id},
        headers=auth_headers,
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(tx["type"] == "income" for tx in items)


@pytest.mark.asyncio
async def test_filter_transactions_by_date(client, auth_headers):
    acc_id = await _create_account(client, auth_headers, "Date Filter Acc")

    await client.post(
        "/api/v1/transactions",
        json={"account_id": acc_id, "type": "expense", "amount": "75.00", "currency": "USD", "date": "2024-03-15"},
        headers=auth_headers,
    )

    # Filter to same date range
    response = await client.get(
        "/api/v1/transactions",
        params={"from_date": "2024-03-01", "to_date": "2024-03-31", "account_id": acc_id},
        headers=auth_headers,
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) >= 1

    # Filter to a different range — should not appear
    response2 = await client.get(
        "/api/v1/transactions",
        params={"from_date": "2024-04-01", "to_date": "2024-04-30", "account_id": acc_id},
        headers=auth_headers,
    )
    assert response2.json()["total"] == 0
