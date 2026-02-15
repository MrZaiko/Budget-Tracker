"""Background job: log upcoming subscription renewals (v1: log only)."""

import logging
from datetime import date, timedelta

from app.db.session import AsyncSessionLocal
from app.repositories.recurring import RecurringRepository

logger = logging.getLogger(__name__)
ALERT_DAYS = 7


async def send_subscription_alerts() -> None:
    """Log subscriptions renewing within ALERT_DAYS days. V1 is log-only."""
    today = date.today()
    cutoff = today + timedelta(days=ALERT_DAYS)
    logger.info("Checking subscription alerts for renewals through %s", cutoff)

    async with AsyncSessionLocal() as session:
        try:
            repo = RecurringRepository(session)
            # Get all active subscriptions due within alert window
            from sqlalchemy import select
            from app.models.recurring import RecurringRule
            from sqlalchemy.ext.asyncio import AsyncSession

            result = await session.execute(
                select(RecurringRule).where(
                    RecurringRule.is_subscription.is_(True),
                    RecurringRule.status == "active",
                    RecurringRule.next_occurrence <= cutoff,
                )
            )
            subs = result.scalars().all()

            for sub in subs:
                days_until = (sub.next_occurrence - today).days
                logger.info(
                    "Subscription alert: rule_id=%s name=%s user_id=%s amount=%s %s due_in=%d_days",
                    sub.id,
                    sub.name,
                    sub.user_id,
                    sub.amount,
                    sub.currency,
                    days_until,
                )

            logger.info("Subscription alert check complete: %d upcoming renewals", len(list(subs)))
        except Exception as exc:
            logger.error("Error checking subscription alerts: %s", exc)
