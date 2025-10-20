"""Add investigation_metadata column

Revision ID: 004_investigation_metadata
Revises: 003_performance_indexes
Create Date: 2025-10-20 10:45:00.000000

"""

import sqlalchemy as sa
from sqlalchemy import JSON

from alembic import op

# revision identifiers, used by Alembic.
revision = "004_investigation_metadata"
down_revision = "003_performance_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add investigation_metadata column to investigations table"""

    # Check if column already exists (for idempotency)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("investigations")]

    if "investigation_metadata" not in columns:
        # Add investigation_metadata column using generic JSON type
        op.add_column(
            "investigations",
            sa.Column(
                "investigation_metadata",
                JSON,
                nullable=True,
                server_default="{}",
                comment="Additional metadata for the investigation",
            ),
        )

        # Only create GIN index on PostgreSQL
        if conn.dialect.name == "postgresql":
            op.execute(
                "CREATE INDEX IF NOT EXISTS ix_investigations_metadata "
                "ON investigations USING gin (investigation_metadata)"
            )


def downgrade() -> None:
    """Remove investigation_metadata column"""

    conn = op.get_bind()

    # Drop index if on PostgreSQL
    if conn.dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS ix_investigations_metadata")

    # Drop the column
    op.drop_column("investigations", "investigation_metadata")
