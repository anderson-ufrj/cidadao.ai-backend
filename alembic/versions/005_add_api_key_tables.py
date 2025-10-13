"""Add API key tables

Revision ID: 005
Revises: 004
Create Date: 2025-01-25 10:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "005"
down_revision = "003_performance_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create API key tables."""
    # Create api_keys table
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("key_prefix", sa.String(10), nullable=False),
        sa.Column("key_hash", sa.String(128), nullable=False, unique=True),
        # Status and tier
        sa.Column("status", sa.String(20), nullable=False, default="active"),
        sa.Column("tier", sa.String(20), nullable=False, default="free"),
        # Ownership
        sa.Column("client_id", sa.String(255), nullable=False),
        sa.Column("client_name", sa.String(255)),
        sa.Column("client_email", sa.String(255)),
        # Validity
        sa.Column("expires_at", sa.DateTime()),
        sa.Column("last_used_at", sa.DateTime()),
        sa.Column("last_rotated_at", sa.DateTime()),
        sa.Column("rotation_period_days", sa.Integer(), default=90),
        # Security
        sa.Column("allowed_ips", sa.JSON(), default=[]),
        sa.Column("allowed_origins", sa.JSON(), default=[]),
        sa.Column("scopes", sa.JSON(), default=[]),
        # Rate limiting
        sa.Column("rate_limit_per_minute", sa.Integer()),
        sa.Column("rate_limit_per_hour", sa.Integer()),
        sa.Column("rate_limit_per_day", sa.Integer()),
        # Usage tracking
        sa.Column("total_requests", sa.Integer(), default=0),
        sa.Column("total_errors", sa.Integer(), default=0),
        sa.Column("last_error_at", sa.DateTime()),
        # Metadata
        sa.Column("metadata", sa.JSON(), default={}),
        # Timestamps
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
    )

    # Create indexes
    op.create_index("ix_api_keys_client_id", "api_keys", ["client_id"])
    op.create_index("ix_api_keys_status", "api_keys", ["status"])
    op.create_index("ix_api_keys_expires_at", "api_keys", ["expires_at"])

    # Create api_key_rotations table
    op.create_table(
        "api_key_rotations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "api_key_id", sa.String(36), sa.ForeignKey("api_keys.id"), nullable=False
        ),
        sa.Column("old_key_hash", sa.String(128), nullable=False),
        sa.Column("new_key_hash", sa.String(128), nullable=False),
        sa.Column("rotation_reason", sa.String(255)),
        sa.Column("initiated_by", sa.String(255)),
        sa.Column("grace_period_hours", sa.Integer(), default=24),
        sa.Column("old_key_expires_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime()),
        # Timestamps
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
    )

    # Create index on api_key_id
    op.create_index(
        "ix_api_key_rotations_api_key_id", "api_key_rotations", ["api_key_id"]
    )


def downgrade() -> None:
    """Drop API key tables."""
    op.drop_index("ix_api_key_rotations_api_key_id", "api_key_rotations")
    op.drop_table("api_key_rotations")

    op.drop_index("ix_api_keys_expires_at", "api_keys")
    op.drop_index("ix_api_keys_status", "api_keys")
    op.drop_index("ix_api_keys_client_id", "api_keys")
    op.drop_table("api_keys")
