"""Unit tests for auth service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.auth import get_or_create_user, issue_local_token, validate_local_token


def test_issue_and_validate_local_token():
    with patch("app.services.auth.settings") as mock_settings:
        mock_settings.local_auth_secret = "test-secret-key-32-chars-minimum!!"
        mock_settings.oidc_issuer_url = ""
        mock_settings.oidc_audience = ""

        token = issue_local_token(
            sub="local:test@example.com",
            email="test@example.com",
            display_name="Test User",
        )
        assert isinstance(token, str)

        claims = validate_local_token(token)
        assert claims["sub"] == "local:test@example.com"
        assert claims["email"] == "test@example.com"
        assert claims["iss"] == "local"


@pytest.mark.asyncio
async def test_get_or_create_user_existing():
    """Returns existing user without creating a new one."""
    existing_user = MagicMock()
    existing_user.id = uuid.uuid4()
    existing_user.sub = "existing-sub"

    mock_repo = AsyncMock()
    mock_repo.get_by_sub.return_value = existing_user

    claims = {"sub": "existing-sub", "email": "existing@example.com", "name": "Existing"}
    result = await get_or_create_user(claims, mock_repo, "oidc")

    assert result is existing_user
    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_user_new():
    """Creates a new user when sub not found."""
    new_user = MagicMock()
    new_user.id = uuid.uuid4()

    mock_repo = AsyncMock()
    mock_repo.get_by_sub.return_value = None
    mock_repo.create.return_value = new_user

    with patch("app.services.auth.settings") as mock_settings:
        mock_settings.base_currency = "USD"

        claims = {"sub": "new-sub", "email": "new@example.com", "name": "New User"}
        result = await get_or_create_user(claims, mock_repo, "oidc")

    assert result is new_user
    mock_repo.create.assert_called_once()
    call_kwargs = mock_repo.create.call_args.kwargs
    assert call_kwargs["sub"] == "new-sub"
    assert call_kwargs["email"] == "new@example.com"
    assert call_kwargs["auth_provider"] == "oidc"
