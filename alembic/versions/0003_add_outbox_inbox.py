"""Add outbox and inbox tables

Revision ID: 0003_add_outbox_inbox
Revises: 0002_add_payment_id
Create Date: 2026-08-25
"""

import sqlalchemy as sa
from alembic import op

revision = "0003_add_outbox_inbox"
down_revision = "0002_add_payment_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "outbox",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column(
            "attempts_number", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("error", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_outbox_status_created_at",
        "outbox",
        ["status", "created_at"],
    )

    op.create_table(
        "inbox",
        sa.Column("id", sa.String(96), primary_key=True),
        sa.Column("topic", sa.String(128), nullable=False),
        sa.Column("partition", sa.Integer(), nullable=False),
        sa.Column("offset", sa.BigInteger(), nullable=False),
        sa.Column(
            "processed_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.UniqueConstraint(
            "topic", "partition", "offset", name="uq_inbox_message"
        ),
    )


def downgrade() -> None:
    op.drop_table("inbox")
    op.drop_index("ix_outbox_status_created_at", table_name="outbox")
    op.drop_table("outbox")
