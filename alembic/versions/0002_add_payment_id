"""Add payment_id to orders

Revision ID: 0002_add_payment_id
Revises: 0001_initial
Create Date: 2026-08-24
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_add_payment_id"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("payment_id", sa.String(64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("orders", "payment_id")
