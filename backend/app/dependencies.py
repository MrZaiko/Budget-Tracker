from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import get_or_create_user, validate_local_token, validate_oidc_token

settings = get_settings()
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    token = credentials.credentials
    try:
        # Peek at the issuer without full validation
        from jose import jwt as jose_jwt

        unverified = jose_jwt.get_unverified_claims(token)
        iss = unverified.get("iss", "")

        if iss == "local":
            if not settings.local_auth_enabled:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "detail": "Local auth is disabled",
                        "code": "local_auth_disabled",
                    },
                )
            claims = validate_local_token(token)
            auth_provider = "local"
        else:
            claims = await validate_oidc_token(token)
            auth_provider = "oidc"

    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail={"detail": "Invalid or expired token", "code": "invalid_token"},
        ) from exc

    user_repo = UserRepository(session)
    return await get_or_create_user(claims, user_repo, auth_provider)


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail={"code": "admin_required"})
    return user
