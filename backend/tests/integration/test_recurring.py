"""Integration tests for recurring rules and subscriptions endpoints."""

import uuid
from datetime import date, timedelta

import pytest


def _make_rule_payload(account_id: uuid.UUID, **overrides) -> dict:
    base = {
        "account_id": str(account_id),
        "name": "Netflix",
        "type": "expense",
        "amount": "15.99",
        "currency": "USD",
        "frequency": "monthly",
        "start_date": str(date.today()),
        "is_subscription": False,
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_list_recurring_empty(client, auth_headers):
    response = await client.get("/api/v1/recurring", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_recurring_rule(client, auth_headers):
    # Create an account first
    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Recurring Acc", "type": "checking", "currency": "USD"},
        headers=auth_headers,
    )
    acc_id = acc_resp.json()["id"]

    payload = _make_rule_payload(acc_id, name="Rent", amount="1200.00", frequency="monthly")
    response = await client.post("/api/v1/recurring", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Rent"
    assert data["frequency"] == "monthly"
    assert data["status"] == "active"
    assert data["next_occurrence"] == str(date.today())


@pytest.mark.asyncio
async def test_get_recurring_rule(client, auth_headers):
    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Acc2", "type": "checking", "currency": "USD"},
        headers=auth_headers,
    )
    acc_id = acc_resp.json()["id"]

    create_resp = await client.post(
        "/api/v1/recurring",
        json=_make_rule_payload(acc_id, name="Spotify"),
        headers=auth_headers,
    )
    rule_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/recurring/{rule_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Spotify"


@pytest.mark.asyncio
async def test_get_recurring_not_found(client, auth_headers):
    response = await client.get(f"/api/v1/recurring/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


@pytest.mark.asyncio
async def test_update_recurring_rule(client, auth_headers):
    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Acc3", "type": "checking", "currency": "USD"},
        headers=auth_headers,
    )
    acc_id = acc_resp.json()["id"]

    create_resp = await client.post(
        "/api/v1/recurring",
        json=_make_rule_payload(acc_id, name="Old Name"),
        headers=auth_headers,
    )
    rule_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/recurring/{rule_id}",
        json={"name": "Updated Name", "amount": "20.00"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_recurring_rule(client, auth_headers):
    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Acc4", "type": "checking", "currency": "USD"},
        headers=auth_headers,
    )
    acc_id = acc_resp.json()["id"]

    create_resp = await client.post(
        "/api/v1/recurring",
        json=_make_rule_payload(acc_id, name="ToDelete"),
        headers=auth_headers,
    )
    rule_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/recurring/{rule_id}", headers=auth_headers)
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_list_subscriptions_empty(client, auth_headers):
    response = await client.get("/api/v1/subscriptions", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_subscription_appears_in_subscriptions(client, auth_headers):
    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Acc5", "type": "checking", "currency": "USD"},
        headers=auth_headers,
    )
    acc_id = acc_resp.json()["id"]

    await client.post(
        "/api/v1/recurring",
        json=_make_rule_payload(acc_id, name="Disney+", is_subscription=True),
        headers=auth_headers,
    )

    subs_resp = await client.get("/api/v1/subscriptions", headers=auth_headers)
    assert subs_resp.status_code == 200
    names = [s["name"] for s in subs_resp.json()]
    assert "Disney+" in names


@pytest.mark.asyncio
async def test_upcoming_subscriptions(client, auth_headers):
    acc_resp = await client.post(
        "/api/v1/accounts",
        json={"name": "Acc6", "type": "checking", "currency": "USD"},
        headers=auth_headers,
    )
    acc_id = acc_resp.json()["id"]

    # Create a subscription due today
    await client.post(
        "/api/v1/recurring",
        json=_make_rule_payload(
            acc_id,
            name="Apple Music",
            is_subscription=True,
            start_date=str(date.today()),
        ),
        headers=auth_headers,
    )

    upcoming_resp = await client.get(
        "/api/v1/subscriptions/upcoming",
        params={"days": 30},
        headers=auth_headers,
    )
    assert upcoming_resp.status_code == 200
    names = [s["name"] for s in upcoming_resp.json()]
    assert "Apple Music" in names
