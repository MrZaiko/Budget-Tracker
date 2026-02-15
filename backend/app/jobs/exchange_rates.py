"""Background job: fetch and cache exchange rates from Frankfurter API."""

import logging
import uuid
from datetime import date, datetime, timezone

import httpx
from sqlalchemy import text

from app.config import get_settings
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)
settings = get_settings()

# Bases to fetch so that lookups by any common user base_currency work.
_BASES_TO_FETCH = ["EUR", "USD", "GBP", "CHF", "JPY", "CAD", "AUD"]


async def _fetch_for_base(client: httpx.AsyncClient, base: str) -> tuple[str, date, dict] | None:
    url = f"{settings.frankfurter_base_url}/latest?base={base}"
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
        return data.get("base", base), date.fromisoformat(data["date"]), data.get("rates", {})
    except Exception as exc:
        logger.warning("Failed to fetch rates for base=%s: %s", base, exc)
        return None


async def refresh_exchange_rates() -> None:
    """Fetch latest rates for multiple base currencies and upsert. Idempotent."""
    logger.info("Starting exchange rate refresh")

    async with httpx.AsyncClient(timeout=30) as client:
        results = []
        for base in _BASES_TO_FETCH:
            result = await _fetch_for_base(client, base)
            if result:
                results.append(result)

    if not results:
        logger.error("No exchange rates could be fetched")
        return

    now = datetime.now(timezone.utc).isoformat()
    async with AsyncSessionLocal() as session:
        try:
            for base, rate_date, rates in results:
                for target, rate in rates.items():
                    await session.execute(
                        text(
                            """
                            INSERT INTO exchange_rates (id, base_currency, target_currency, rate, date, fetched_at)
                            VALUES (:id, :base, :target, :rate, :date, :fetched_at)
                            ON CONFLICT (base_currency, target_currency, date)
                            DO UPDATE SET rate = EXCLUDED.rate, fetched_at = EXCLUDED.fetched_at
                            """
                        ),
                        {
                            "id": str(uuid.uuid4()),
                            "base": base,
                            "target": target,
                            "rate": rate,
                            "date": rate_date,
                            "fetched_at": now,
                        },
                    )
            await session.commit()
            total = sum(len(r[2]) for r in results)
            logger.info("Exchange rates refreshed: %d rows across %d bases", total, len(results))
        except Exception as exc:
            await session.rollback()
            logger.error("Failed to store exchange rates: %s", exc)
