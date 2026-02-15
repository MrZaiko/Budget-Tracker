import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import DATE, NUMERIC, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.budget import Budget
    from app.models.category import Category
    from app.models.recurring import RecurringRule
    from app.models.user import User


class Transaction(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_transactions_user_date", "user_id", "date"),
        Index("ix_transactions_account_id", "account_id"),
        Index("ix_transactions_budget_id", "budget_id"),
        Index("ix_transactions_category_id", "category_id"),
        Index("ix_transactions_recurring_rule_id", "recurring_rule_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("users.id"), nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("accounts.id"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("categories.id"), nullable=True
    )
    budget_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("budgets.id"), nullable=True
    )
    recurring_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("recurring_rules.id"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # income, expense, transfer
    amount: Mapped[float] = mapped_column(NUMERIC(18, 6), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), ForeignKey("currencies.code"), nullable=False)
    # account_currency / amount_account: amount expressed in the account's currency (snapshotted at write time)
    account_currency: Mapped[str | None] = mapped_column(String(3), ForeignKey("currencies.code"), nullable=True)
    amount_account: Mapped[float | None] = mapped_column(NUMERIC(18, 6), nullable=True)
    account_exchange_rate: Mapped[float | None] = mapped_column(NUMERIC(18, 8), nullable=True)
    # amount_base / exchange_rate: amount expressed in the user's base currency (snapshotted at write time)
    amount_base: Mapped[float] = mapped_column(NUMERIC(18, 6), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(NUMERIC(18, 8), nullable=False)
    date: Mapped[date] = mapped_column(DATE, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    transfer_to_account_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("accounts.id"), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    account: Mapped["Account"] = relationship(
        "Account",
        foreign_keys=[account_id],
        back_populates="transactions",
    )
    transfer_to_account: Mapped["Account | None"] = relationship(
        "Account",
        foreign_keys=[transfer_to_account_id],
        back_populates="transfer_transactions",
    )
    category: Mapped["Category | None"] = relationship("Category", back_populates="transactions")
    budget: Mapped["Budget | None"] = relationship("Budget", back_populates="transactions")
    recurring_rule: Mapped["RecurringRule | None"] = relationship(
        "RecurringRule", back_populates="transactions"
    )
