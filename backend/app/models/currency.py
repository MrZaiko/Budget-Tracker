import uuid
from datetime import date, datetime

from sqlalchemy import DATE, NUMERIC, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPkMixin


class Currency(Base):
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(8), nullable=False)

    # Relationships
    exchange_rates_base: Mapped[list["ExchangeRate"]] = relationship(
        "ExchangeRate",
        foreign_keys="ExchangeRate.base_currency",
        back_populates="base_currency_rel",
    )
    exchange_rates_target: Mapped[list["ExchangeRate"]] = relationship(
        "ExchangeRate",
        foreign_keys="ExchangeRate.target_currency",
        back_populates="target_currency_rel",
    )


class ExchangeRate(Base, UUIDPkMixin):
    __tablename__ = "exchange_rates"
    __table_args__ = (
        UniqueConstraint("base_currency", "target_currency", "date", name="uq_exchange_rate"),
    )

    base_currency: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.code"), nullable=False
    )
    target_currency: Mapped[str] = mapped_column(
        String(3), ForeignKey("currencies.code"), nullable=False
    )
    rate: Mapped[float] = mapped_column(NUMERIC(18, 8), nullable=False)
    date: Mapped[date] = mapped_column(DATE, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    base_currency_rel: Mapped["Currency"] = relationship(
        "Currency",
        foreign_keys=[base_currency],
        back_populates="exchange_rates_base",
    )
    target_currency_rel: Mapped["Currency"] = relationship(
        "Currency",
        foreign_keys=[target_currency],
        back_populates="exchange_rates_target",
    )
