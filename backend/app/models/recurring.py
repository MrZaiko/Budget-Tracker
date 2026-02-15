import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BOOLEAN, DATE, NUMERIC, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.budget import Budget
    from app.models.category import Category
    from app.models.transaction import Transaction
    from app.models.user import User


class RecurringRule(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "recurring_rules"
    __table_args__ = (
        Index("ix_recurring_rules_user_status_next", "user_id", "status", "next_occurrence"),
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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # income, expense
    amount: Mapped[float] = mapped_column(NUMERIC(18, 6), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), ForeignKey("currencies.code"), nullable=False)
    frequency: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # daily, weekly, monthly, yearly
    start_date: Mapped[date] = mapped_column(DATE, nullable=False)
    end_date: Mapped[date | None] = mapped_column(DATE, nullable=True)
    next_occurrence: Mapped[date] = mapped_column(DATE, nullable=False)
    is_subscription: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")  # active, paused, cancelled
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="recurring_rules")
    account: Mapped["Account"] = relationship("Account")
    category: Mapped["Category | None"] = relationship("Category")
    budget: Mapped["Budget | None"] = relationship("Budget")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="recurring_rule"
    )
