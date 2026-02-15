import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.budget import Budget, BudgetCollaborator
    from app.models.category import Category
    from app.models.recurring import RecurringRule
    from app.models.transaction import Transaction


class User(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "users"

    sub: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    base_currency: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.code"), nullable=False
    )
    auth_provider: Mapped[str] = mapped_column(String(16), nullable=False)  # 'oidc' | 'local'
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, server_default="false")

    # Relationships
    local_user: Mapped["LocalUser | None"] = relationship("LocalUser", back_populates="user", uselist=False)
    accounts: Mapped[list["Account"]] = relationship("Account", back_populates="user")
    categories: Mapped[list["Category"]] = relationship("Category", back_populates="user")
    budgets: Mapped[list["Budget"]] = relationship(
        "Budget", foreign_keys="Budget.owner_id", back_populates="owner"
    )
    budget_collaborations: Mapped[list["BudgetCollaborator"]] = relationship(
        "BudgetCollaborator", back_populates="user"
    )
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user")
    recurring_rules: Mapped[list["RecurringRule"]] = relationship(
        "RecurringRule", back_populates="user"
    )


class LocalUser(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "local_users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("users.id"), unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="local_user")
