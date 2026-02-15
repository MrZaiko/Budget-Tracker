"""add_account_currency_to_transactions

Revision ID: 0003
Revises: 0002
Create Date: 2026-02-14 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("account_currency", sa.String(3), sa.ForeignKey("currencies.code"), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column("amount_account", sa.Numeric(18, 6), nullable=True),
    )
    op.add_column(
        "transactions",
        sa.Column("account_exchange_rate", sa.Numeric(18, 8), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("transactions", "account_exchange_rate")
    op.drop_column("transactions", "amount_account")
    op.drop_column("transactions", "account_currency")
