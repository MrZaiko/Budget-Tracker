"""Integration tests for categories endpoints."""

import uuid

import pytest


@pytest.mark.asyncio
async def test_list_categories_empty(client, auth_headers):
    response = await client.get("/api/v1/categories", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_category(client, auth_headers):
    payload = {
        "name": "Groceries",
        "icon": "shopping_cart",
        "color": "#4CAF50",
        "transaction_type": "expense",
    }
    response = await client.post("/api/v1/categories", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Groceries"
    assert data["color"] == "#4CAF50"
    assert data["transaction_type"] == "expense"
    assert data["is_system"] is False
    assert "id" in data


@pytest.mark.asyncio
async def test_create_category_minimal(client, auth_headers):
    payload = {"name": "Misc"}
    response = await client.post("/api/v1/categories", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Misc"
    assert data["transaction_type"] == "both"


@pytest.mark.asyncio
async def test_create_and_list_category(client, auth_headers):
    payload = {"name": "Entertainment", "transaction_type": "expense"}
    await client.post("/api/v1/categories", json=payload, headers=auth_headers)

    list_response = await client.get("/api/v1/categories", headers=auth_headers)
    assert list_response.status_code == 200
    names = [c["name"] for c in list_response.json()]
    assert "Entertainment" in names


@pytest.mark.asyncio
async def test_update_category(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/categories",
        json={"name": "Old Name", "transaction_type": "expense"},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    cat_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/categories/{cat_id}",
        json={"name": "New Name", "color": "#FF5722"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["name"] == "New Name"
    assert data["color"] == "#FF5722"


@pytest.mark.asyncio
async def test_update_category_not_found(client, auth_headers):
    response = await client.patch(
        f"/api/v1/categories/{uuid.uuid4()}",
        json={"name": "Ghost"},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


@pytest.mark.asyncio
async def test_delete_category(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/categories",
        json={"name": "ToDelete", "transaction_type": "expense"},
        headers=auth_headers,
    )
    cat_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/categories/{cat_id}", headers=auth_headers)
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_category_not_found(client, auth_headers):
    response = await client.delete(
        f"/api/v1/categories/{uuid.uuid4()}", headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
