"""Integration test for health endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    # Health may report db error in test env, but endpoint itself should respond
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "db" in data
    assert "scheduler" in data
