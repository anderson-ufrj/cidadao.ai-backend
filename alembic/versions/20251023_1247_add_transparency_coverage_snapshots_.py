"""Add transparency coverage snapshots table

Revision ID: 97f22967055b
Revises: 77f2e2dbf0ba
Create Date: 2025-10-23 12:47:15.085236-03:00

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "97f22967055b"
down_revision = "77f2e2dbf0ba"
branch_labels = None
depends_on = None


def upgrade():
    # Create transparency_coverage_snapshots table
    op.create_table(
        "transparency_coverage_snapshots",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("snapshot_date", sa.DateTime(), nullable=False),
        sa.Column("coverage_data", sa.JSON(), nullable=False),
        sa.Column("summary_stats", sa.JSON(), nullable=False),
        sa.Column("state_code", sa.String(length=2), nullable=True),
        sa.Column("state_status", sa.String(length=20), nullable=True),
        sa.Column("coverage_percentage", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        comment="Transparency API coverage snapshots for Brazil map visualization",
    )

    # Create indexes for performance
    op.create_index(
        "idx_snapshot_date_desc",
        "transparency_coverage_snapshots",
        [sa.text("snapshot_date DESC")],
        unique=False,
    )
    op.create_index(
        "idx_state_coverage",
        "transparency_coverage_snapshots",
        ["state_code", "coverage_percentage"],
        unique=False,
    )
    op.create_index(
        "idx_state_date",
        "transparency_coverage_snapshots",
        [sa.text("state_code, snapshot_date DESC")],
        unique=False,
    )
    op.create_index(
        "ix_transparency_coverage_snapshots_snapshot_date",
        "transparency_coverage_snapshots",
        ["snapshot_date"],
        unique=False,
    )
    op.create_index(
        "ix_transparency_coverage_snapshots_state_code",
        "transparency_coverage_snapshots",
        ["state_code"],
        unique=False,
    )


def downgrade():
    # Drop indexes first
    op.drop_index(
        "ix_transparency_coverage_snapshots_state_code",
        table_name="transparency_coverage_snapshots",
    )
    op.drop_index(
        "ix_transparency_coverage_snapshots_snapshot_date",
        table_name="transparency_coverage_snapshots",
    )
    op.drop_index("idx_state_date", table_name="transparency_coverage_snapshots")
    op.drop_index("idx_state_coverage", table_name="transparency_coverage_snapshots")
    op.drop_index(
        "idx_snapshot_date_desc", table_name="transparency_coverage_snapshots"
    )

    # Drop table
    op.drop_table("transparency_coverage_snapshots")
