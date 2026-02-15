"""Background job: generate transactions for due recurring rules."""

import logging
from datetime import date
from decimal import Decimal

from app.db.session import AsyncSessionLocal
from app.repositories.currency import ExchangeRateRepository
from app.repositories.recurring import RecurringRepository
from app.repositories.transaction import TransactionRepository
from app.repositories.user import UserRepository
from app.utils.currency import get_rate_or_1
from app.utils.date_utils import next_occurrence

logger = logging.getLogger(__name__)


async def generate_recurring_transactions() -> None:
    """Create transactions for all active recurring rules due today. Idempotent."""
    today = date.today()
    logger.info("Generating recurring transactions for %s", today)

    async with AsyncSessionLocal() as session:
        try:
            recurring_repo = RecurringRepository(session)
            tx_repo = TransactionRepository(session)
            rate_repo = ExchangeRateRepository(session)
            user_repo = UserRepository(session)

            due_rules = await recurring_repo.get_due_today(today)
            logger.info("Found %d due rules", len(due_rules))

            for rule in due_rules:
                # Skip if already generated for today (idempotency)
                if await tx_repo.exists_for_rule_and_date(rule.id, today):
                    logger.debug("Skipping rule %s: already has transaction for %s", rule.id, today)
                    # Still advance next_occurrence if needed
                    if rule.next_occurrence <= today:
                        rule.next_occurrence = next_occurrence(today, rule.frequency)
                        session.add(rule)
                    continue

                # Get user base currency for amount_base
                user = await user_repo.get(rule.user_id)
                base_currency = user.base_currency if user else "USD"

                rate = await get_rate_or_1(rate_repo, rule.currency, base_currency)
                amount = Decimal(str(rule.amount))
                amount_base = amount * rate

                await tx_repo.create(
                    user_id=rule.user_id,
                    account_id=rule.account_id,
                    category_id=rule.category_id,
                    budget_id=rule.budget_id,
                    recurring_rule_id=rule.id,
                    type=rule.type,
                    amount=amount,
                    currency=rule.currency,
                    amount_base=amount_base,
                    exchange_rate=rate,
                    date=today,
                    notes=f"Auto-generated from recurring rule: {rule.name}",
                )

                # Advance next_occurrence
                new_next = next_occurrence(today, rule.frequency)
                # Cancel if past end_date
                if rule.end_date and new_next > rule.end_date:
                    rule.status = "cancelled"
                else:
                    rule.next_occurrence = new_next
                session.add(rule)
                logger.info("Generated transaction for rule %s (%s)", rule.id, rule.name)

            await session.commit()
            logger.info("Recurring transaction generation complete")

        except Exception as exc:
            await session.rollback()
            logger.error("Error generating recurring transactions: %s", exc)
            raise
