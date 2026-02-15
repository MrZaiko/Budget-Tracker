from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db
from app.repositories.user import LocalUserRepository
from app.schemas.auth import LocalTokenRequest, TokenResponse
from app.services.auth import issue_local_token

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/local/token", response_model=TokenResponse)
async def local_token(
    data: LocalTokenRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    if not settings.local_auth_enabled:
        raise HTTPException(
            status_code=403,
            detail={"detail": "Local auth is disabled", "code": "local_auth_disabled"},
        )

    import bcrypt

    repo = LocalUserRepository(session)
    local_user = await repo.get_by_email(data.email)
    if not local_user:
        raise HTTPException(
            status_code=401,
            detail={"detail": "Invalid credentials", "code": "invalid_credentials"},
        )

    password_valid = bcrypt.checkpw(
        data.password.encode(), local_user.password_hash.encode()
    )
    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail={"detail": "Invalid credentials", "code": "invalid_credentials"},
        )

    # Get the associated user for display name
    from app.repositories.user import UserRepository
    user_repo = UserRepository(session)
    user = await user_repo.get(local_user.user_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail={"detail": "Invalid credentials", "code": "invalid_credentials"},
        )

    token = issue_local_token(
        sub=f"local:{user.email}",
        email=user.email,
        display_name=user.display_name,
    )
    return TokenResponse(access_token=token)
