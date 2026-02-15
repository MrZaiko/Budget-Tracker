import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DATE, NUMERIC, DateTime, ForeignKey, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.transaction import Transaction
    from app.models.user import User


class Budget(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "budgets"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    period_type: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # monthly, weekly, yearly, custom
    start_date: Mapped[date] = mapped_column(DATE, nullable=False)
    end_date: Mapped[date | None] = mapped_column(DATE, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), ForeignKey("currencies.code"), nullable=False)

    # Relationships
    owner: Mapped["User"] = relationship(
        "User", foreign_keys=[owner_id], back_populates="budgets"
    )
    budget_categories: Mapped[list["BudgetCategory"]] = relationship(
        "BudgetCategory", back_populates="budget", cascade="all, delete-orphan"
    )
    collaborators: Mapped[list["BudgetCollaborator"]] = relationship(
        "BudgetCollaborator", back_populates="budget", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="budget"
    )


class BudgetCategory(Base, UUIDPkMixin):
    __tablename__ = "budget_categories"
    __table_args__ = (
        UniqueConstraint("budget_id", "category_id", name="uq_budget_category"),
    )

    budget_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("budgets.id"), nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("categories.id"), nullable=False
    )
    limit_amount: Mapped[float] = mapped_column(NUMERIC(18, 6), nullable=False)

    # Relationships
    budget: Mapped["Budget"] = relationship("Budget", back_populates="budget_categories")
    category: Mapped["Category"] = relationship("Category", back_populates="budget_categories")


class BudgetCollaborator(Base, UUIDPkMixin):
    __tablename__ = "budget_collaborators"
    __table_args__ = (
        UniqueConstraint("budget_id", "user_id", name="uq_budget_collaborator"),
    )

    budget_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("budgets.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("users.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # viewer, editor
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    budget: Mapped["Budget"] = relationship("Budget", back_populates="collaborators")
    user: Mapped["User"] = relationship("User", back_populates="budget_collaborations")
