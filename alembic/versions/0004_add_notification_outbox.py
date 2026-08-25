"""Add notification_outbox table

Revision ID: 0004_add_notification_outbox
Revises: 0003_add_outbox_inbox
Create Date: 2026-08-25
"""

import sqlalchemy as sa
from alembic import op

revision = "0004_add_notification_outbox"
down_revision = "0003_add_outbox_inbox"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_outbox",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("message", sa.String(1024), nullable=False),
        sa.Column("reference_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column(
            "attempts_number",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("error", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_notification_outbox_status_created_at",
        "notification_outbox",
        ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notification_outbox_status_created_at",
        table_name="notification_outbox",
    )
    op.drop_table("notification_outbox")
