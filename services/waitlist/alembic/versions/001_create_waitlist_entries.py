"""create waitlist entries table

Revision ID: 001
Revises:
Create Date: 2026-03-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS waitlist")

    op.create_table(
        "entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        schema="waitlist",
    )

    op.execute(
        "CREATE UNIQUE INDEX unique_email_lower ON waitlist.entries (LOWER(email))"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS waitlist.unique_email_lower")
    op.drop_table("entries", schema="waitlist")
    op.execute("DROP SCHEMA IF EXISTS waitlist")
