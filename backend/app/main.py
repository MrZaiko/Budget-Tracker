import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.db.seed import seed_currencies, seed_exchange_rates
from app.db.session import AsyncSessionLocal
from app.jobs.scheduler import setup_scheduler
from app.middleware.error_handler import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.middleware.logging import LoggingMiddleware
from app.routers import (
    accounts,
    admin,
    auth,
    budgets,
    categories,
    currencies,
    recurring,
    reports,
    transactions,
    users,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    # Startup
    logger.info("Starting Budget Tracker API")

    from app.db.session import engine, _is_sqlite

    if _is_sqlite:
        # In-memory SQLite: create schema directly (Alembic is not used)
        from app.db.base import Base
        import app.models  # noqa: F401 — ensure all models are registered
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite in-memory schema created")

    async with AsyncSessionLocal() as session:
        await seed_currencies(session)
        logger.info("Currencies seeded")
        await seed_exchange_rates(session)
        logger.info("Exchange rates bootstrapped")

    # Fetch live rates immediately so the app starts with fresh data.
    # Runs in the background — startup is not blocked if the API is unreachable.
    from app.jobs.exchange_rates import refresh_exchange_rates
    import asyncio
    asyncio.ensure_future(refresh_exchange_rates())

    if _is_sqlite and settings.local_auth_enabled:
        await _seed_dev_user()

    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("Scheduler started")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")


async def _seed_dev_user() -> None:
    """Create the default dev user in the in-memory SQLite database.

    This must run inside the server process so it shares the same StaticPool
    connection as uvicorn — manage.py cannot reach an in-memory database.
    """
    import os
    import bcrypt
    from app.repositories.user import LocalUserRepository, UserRepository

    email = os.environ.get("DEV_EMAIL", "dev@example.com")
    password = os.environ.get("DEV_PASSWORD", "password")
    display_name = os.environ.get("DEV_NAME", "Dev User")
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        local_repo = LocalUserRepository(session)

        existing = await user_repo.get_by_email(email)
        if existing:
            logger.info("Dev user already exists: %s", email)
            return

        is_first = await user_repo.count() == 0
        user = await user_repo.create(
            sub=f"local:{email}",
            email=email,
            display_name=display_name,
            base_currency=settings.base_currency,
            auth_provider="local",
            is_admin=is_first,
        )
        await local_repo.create(
            user_id=user.id,
            email=email,
            password_hash=password_hash,
        )
        await session.commit()
        logger.info("Dev user created: %s", email)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Budget Tracker API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Middleware (CORS must be added first so preflight OPTIONS requests are
    # handled before any other middleware or route matching)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    # Exception handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)

    # Routers (all under /api/v1)
    prefix = "/api/v1"
    app.include_router(auth.router, prefix=prefix)
    app.include_router(admin.router, prefix=prefix)
    app.include_router(users.router, prefix=prefix)
    app.include_router(accounts.router, prefix=prefix)
    app.include_router(categories.router, prefix=prefix)
    app.include_router(transactions.router, prefix=prefix)
    app.include_router(budgets.router, prefix=prefix)
    app.include_router(recurring.router, prefix=prefix)
    app.include_router(currencies.router, prefix=prefix)
    app.include_router(reports.router, prefix=prefix)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, Any]:
        from sqlalchemy import text

        db_ok = False
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
                db_ok = True
        except Exception:
            pass

        from app.jobs.scheduler import scheduler

        return {
            "status": "ok",
            "db": "ok" if db_ok else "error",
            "scheduler": "ok" if scheduler.running else "stopped",
        }

    return app


app = create_app()
