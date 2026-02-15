import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BOOLEAN, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from app.models.budget import BudgetCategory
    from app.models.transaction import Transaction
    from app.models.user import User


class Category(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "categories"
    __table_args__ = (Index("ix_categories_user_id", "user_id"),)

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("users.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    transaction_type: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # income, expense, both
    is_system: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)

    # Relationships
    user: Mapped["User | None"] = relationship("User", back_populates="categories")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="category"
    )
    budget_categories: Mapped[list["BudgetCategory"]] = relationship(
        "BudgetCategory", back_populates="category"
    )
