"""Test fixtures: engine, db session, async client, auth override."""

import os
import uuid

# Set env vars BEFORE any app imports so Settings initializes correctly
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("LOCAL_AUTH_ENABLED", "false")
os.environ.setdefault("LOCAL_AUTH_SECRET", "test-secret-key-that-is-long-enough-32ch")
os.environ.setdefault("OIDC_ISSUER_URL", "https://test.example.com/")
os.environ.setdefault("OIDC_AUDIENCE", "test-audience")

from collections.abc import AsyncGenerator  # noqa: E402
from datetime import datetime, timezone  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from fastapi import Depends  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.exc import IntegrityError  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.dependencies import get_current_user  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Stable UUID for the canonical test user — used as PK so merge() finds the same row.
MOCK_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def _seed_test_user(test_engine):
    """Insert the canonical test user ONCE for the whole session."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    now = datetime.now(timezone.utc)
    async with session_factory() as session:
        try:
            user = User()
            user.id = MOCK_USER_ID
            user.sub = "test|123"
            user.email = "test@example.com"
            user.display_name = "Test User"
            user.base_currency = "USD"
            user.auth_provider = "oidc"
            user.created_at = now
            user.updated_at = now
            session.add(user)
            await session.commit()
        except IntegrityError:
            await session.rollback()  # Already seeded from a previous run


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a test DB session that rolls back after each test."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
def mock_user():
    """A fake User object for auth override (NOT session-tracked)."""
    now = datetime.now(timezone.utc)
    user = User()
    user.id = MOCK_USER_ID
    user.sub = "test|123"
    user.email = "test@example.com"
    user.display_name = "Test User"
    user.base_currency = "USD"
    user.auth_provider = "oidc"
    user.created_at = now
    user.updated_at = now
    return user


@pytest_asyncio.fixture
async def client(mock_user, test_engine, _seed_test_user):
    """AsyncClient with auth and DB dependencies overridden to use test engine.

    `override_get_current_user` loads the user from the *same* request session
    so that `session.add(user)` in services does an UPDATE, not a spurious INSERT.
    """
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def override_get_current_user(session: AsyncSession = Depends(get_db)):
        """Load user from the request session so it's properly identity-mapped.

        Using Depends(get_db) — not override_get_db — ensures FastAPI shares
        the same session instance (keyed by get_db) with the route handler.
        """
        user = await session.get(User, MOCK_USER_ID)
        return user or mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Dummy auth headers (actual auth bypassed by override)."""
    return {"Authorization": "Bearer test-token"}
