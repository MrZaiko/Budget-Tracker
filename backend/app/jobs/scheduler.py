"""APScheduler setup with AsyncIOScheduler."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings
from app.jobs.exchange_rates import refresh_exchange_rates
from app.jobs.recurring_transactions import generate_recurring_transactions
from app.jobs.subscription_alerts import send_subscription_alerts

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)


def setup_scheduler() -> AsyncIOScheduler:
    """Register all cron jobs and return the scheduler."""
    scheduler.add_job(
        refresh_exchange_rates,
        CronTrigger(hour=0, minute=30, timezone=settings.scheduler_timezone),
        id="refresh_exchange_rates",
        replace_existing=True,
        name="Refresh Exchange Rates",
    )
    scheduler.add_job(
        generate_recurring_transactions,
        CronTrigger(hour=1, minute=0, timezone=settings.scheduler_timezone),
        id="generate_recurring_transactions",
        replace_existing=True,
        name="Generate Recurring Transactions",
    )
    scheduler.add_job(
        send_subscription_alerts,
        CronTrigger(hour=8, minute=0, timezone=settings.scheduler_timezone),
        id="send_subscription_alerts",
        replace_existing=True,
        name="Send Subscription Alerts",
    )
    logger.info("Scheduler jobs registered")
    return scheduler
