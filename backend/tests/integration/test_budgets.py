"""Integration tests for budgets endpoints."""

import uuid

import pytest


@pytest.mark.asyncio
async def test_list_budgets_empty(client, auth_headers):
    response = await client.get("/api/v1/budgets", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_budget(client, auth_headers):
    payload = {
        "name": "Monthly Household",
        "period_type": "monthly",
        "start_date": "2024-01-01",
        "currency": "USD",
    }
    response = await client.post("/api/v1/budgets", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Monthly Household"
    assert data["period_type"] == "monthly"
    assert data["currency"] == "USD"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_and_get_budget(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/budgets",
        json={
            "name": "Vacation Fund",
            "period_type": "custom",
            "start_date": "2024-06-01",
            "end_date": "2024-08-31",
            "currency": "EUR",
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    budget_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/v1/budgets/{budget_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Vacation Fund"
    assert get_resp.json()["end_date"] == "2024-08-31"


@pytest.mark.asyncio
async def test_update_budget(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/budgets",
        json={"name": "Old Budget", "period_type": "monthly", "start_date": "2024-01-01", "currency": "USD"},
        headers=auth_headers,
    )
    budget_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/budgets/{budget_id}",
        json={"name": "Updated Budget"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Updated Budget"


@pytest.mark.asyncio
async def test_delete_budget(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/budgets",
        json={"name": "ToDelete", "period_type": "monthly", "start_date": "2024-01-01", "currency": "USD"},
        headers=auth_headers,
    )
    budget_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/budgets/{budget_id}", headers=auth_headers)
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_get_budget_not_found(client, auth_headers):
    response = await client.get(f"/api/v1/budgets/{uuid.uuid4()}", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


@pytest.mark.asyncio
async def test_budget_summary(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/budgets",
        json={"name": "Summary Budget", "period_type": "monthly", "start_date": "2024-01-01", "currency": "USD"},
        headers=auth_headers,
    )
    budget_id = create_resp.json()["id"]

    summary_resp = await client.get(
        f"/api/v1/budgets/{budget_id}/summary", headers=auth_headers
    )
    assert summary_resp.status_code == 200
    data = summary_resp.json()
    assert data["budget_id"] == budget_id
    assert "total_limit" in data
    assert "total_spent" in data
    assert "total_remaining" in data
    assert isinstance(data["categories"], list)


@pytest.mark.asyncio
async def test_list_collaborators_empty(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/budgets",
        json={"name": "Collab Budget", "period_type": "monthly", "start_date": "2024-01-01", "currency": "USD"},
        headers=auth_headers,
    )
    budget_id = create_resp.json()["id"]

    collab_resp = await client.get(
        f"/api/v1/budgets/{budget_id}/collaborators", headers=auth_headers
    )
    assert collab_resp.status_code == 200
    assert collab_resp.json() == []


@pytest.mark.asyncio
async def test_invite_collaborator_user_not_found(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/budgets",
        json={"name": "Budget X", "period_type": "monthly", "start_date": "2024-01-01", "currency": "USD"},
        headers=auth_headers,
    )
    budget_id = create_resp.json()["id"]

    invite_resp = await client.post(
        f"/api/v1/budgets/{budget_id}/collaborators",
        json={"email": "nobody@nowhere.com", "role": "viewer"},
        headers=auth_headers,
    )
    assert invite_resp.status_code == 404
    assert invite_resp.json()["code"] == "user_not_found"


@pytest.mark.asyncio
async def test_create_budget_with_categories(client, auth_headers):
    # Create a category first
    cat_resp = await client.post(
        "/api/v1/categories",
        json={"name": "Food", "transaction_type": "expense"},
        headers=auth_headers,
    )
    cat_id = cat_resp.json()["id"]

    payload = {
        "name": "Budget with cats",
        "period_type": "monthly",
        "start_date": "2024-01-01",
        "currency": "USD",
        "budget_categories": [{"category_id": cat_id, "limit_amount": "500.00"}],
    }
    response = await client.post("/api/v1/budgets", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert len(data["budget_categories"]) == 1
    assert data["budget_categories"][0]["category_id"] == cat_id
