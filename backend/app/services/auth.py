"""Authentication service: OIDC (RS256) + local (HS256)."""

import logging
import time
from typing import Any

import httpx
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.config import get_settings
from app.models.user import User
from app.repositories.user import UserRepository

logger = logging.getLogger(__name__)
settings = get_settings()

# JWKS cache: {issuer_url: {"keys": [...], "fetched_at": timestamp}}
_jwks_cache: dict[str, dict[str, Any]] = {}
JWKS_CACHE_TTL = 3600  # 1 hour


async def _fetch_jwks(issuer_url: str) -> list[dict]:
    """Fetch JWKS from the issuer's well-known endpoint."""
    oidc_config_url = issuer_url.rstrip("/") + "/.well-known/openid-configuration"
    async with httpx.AsyncClient() as client:
        config_resp = await client.get(oidc_config_url, timeout=10)
        config_resp.raise_for_status()
        jwks_uri = config_resp.json()["jwks_uri"]
        jwks_resp = await client.get(jwks_uri, timeout=10)
        jwks_resp.raise_for_status()
        return jwks_resp.json()["keys"]


async def _get_jwks(issuer_url: str, force_refresh: bool = False) -> list[dict]:
    """Return cached JWKS or refresh if expired/forced."""
    cached = _jwks_cache.get(issuer_url)
    if cached and not force_refresh:
        if time.time() - cached["fetched_at"] < JWKS_CACHE_TTL:
            return cached["keys"]  # type: ignore[return-value]

    keys = await _fetch_jwks(issuer_url)
    _jwks_cache[issuer_url] = {"keys": keys, "fetched_at": time.time()}
    return keys


async def validate_oidc_token(token: str) -> dict[str, Any]:
    """Validate a RS256 JWT against the OIDC issuer's JWKS."""
    keys = await _get_jwks(settings.oidc_issuer_url)
    try:
        payload = jwt.decode(
            token,
            keys,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer_url,
        )
        return payload  # type: ignore[no-any-return]
    except JWTError:
        # Retry once with fresh JWKS (key rotation)
        keys = await _get_jwks(settings.oidc_issuer_url, force_refresh=True)
        payload = jwt.decode(
            token,
            keys,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer_url,
        )
        return payload  # type: ignore[no-any-return]


def validate_local_token(token: str) -> dict[str, Any]:
    """Validate a HS256 JWT issued by local auth."""
    payload = jwt.decode(
        token,
        settings.local_auth_secret,
        algorithms=["HS256"],
    )
    return payload  # type: ignore[no-any-return]


def issue_local_token(sub: str, email: str, display_name: str) -> str:
    """Issue a short-lived HS256 JWT for local auth."""
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "email": email,
        "name": display_name,
        "iss": "local",
        "iat": now,
        "exp": now + timedelta(hours=8),
    }
    return jwt.encode(payload, settings.local_auth_secret, algorithm="HS256")  # type: ignore[no-any-return]


async def get_or_create_user(
    claims: dict[str, Any],
    user_repo: UserRepository,
    auth_provider: str,
) -> User:
    """Get existing user by sub or create a new one from token claims."""
    sub = claims["sub"]
    user = await user_repo.get_by_sub(sub)
    if user:
        return user

    email = claims.get("email", "")
    display_name = claims.get("name", email)
    base_currency = settings.base_currency

    is_first = await user_repo.count() == 0
    user = await user_repo.create(
        sub=sub,
        email=email,
        display_name=display_name,
        base_currency=base_currency,
        auth_provider=auth_provider,
        is_admin=is_first,
    )
    return user
