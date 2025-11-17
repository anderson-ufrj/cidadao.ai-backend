"""create investigations table

Revision ID: 0dba430d74c4
Revises: 97f22967055b
Create Date: 2025-11-17 09:51:07.666627-03:00

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0dba430d74c4"
down_revision = "97f22967055b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create investigations table
    op.create_table(
        "investigations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # User identification
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("session_id", sa.String(255), nullable=True, index=True),
        # Investigation details
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("data_source", sa.String(100), nullable=False, index=True),
        # Status tracking
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="pending",
            index=True,
        ),
        sa.Column("current_phase", sa.String(100), nullable=True),
        sa.Column("progress", sa.Float(), server_default="0.0"),
        # Results summary
        sa.Column("anomalies_found", sa.Integer(), server_default="0"),
        sa.Column("total_records_analyzed", sa.Integer(), server_default="0"),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        # JSON data
        sa.Column("filters", sa.JSON(), server_default="{}"),
        sa.Column("anomaly_types", sa.JSON(), server_default="[]"),
        sa.Column("results", sa.JSON(), server_default="[]"),
        sa.Column("investigation_metadata", sa.JSON(), server_default="{}"),
        # Text fields
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        # Timing
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
    )

    # Create indexes
    op.create_index(
        "idx_investigations_user_status", "investigations", ["user_id", "status"]
    )
    op.create_index("idx_investigations_created_at", "investigations", ["created_at"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_investigations_created_at", "investigations")
    op.drop_index("idx_investigations_user_status", "investigations")

    # Drop table
    op.drop_table("investigations")
