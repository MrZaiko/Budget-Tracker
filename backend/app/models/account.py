import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BOOLEAN, NUMERIC, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPkMixin

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.user import User


class Account(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # checking, savings, credit_card, cash, other
    currency: Mapped[str] = mapped_column(String(3), ForeignKey("currencies.code"), nullable=False)
    initial_balance: Mapped[float] = mapped_column(NUMERIC(18, 6), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.account_id",
        back_populates="account",
    )
    transfer_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.transfer_to_account_id",
        back_populates="transfer_to_account",
    )
