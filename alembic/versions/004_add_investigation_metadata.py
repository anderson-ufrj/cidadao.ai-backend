"""Add investigation_metadata column

Revision ID: 004_investigation_metadata
Revises: 003_performance_indexes
Create Date: 2025-10-20 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_investigation_metadata'
down_revision = '003_performance_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add investigation_metadata column to investigations table"""

    # Add investigation_metadata column if it doesn't exist
    op.add_column(
        'investigations',
        sa.Column(
            'investigation_metadata',
            postgresql.JSON,
            nullable=True,
            server_default='{}',
            comment='Additional metadata for the investigation'
        )
    )

    # Create index for better JSON query performance
    op.create_index(
        'ix_investigations_metadata',
        'investigations',
        ['investigation_metadata'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    """Remove investigation_metadata column"""

    # Drop the index first
    op.drop_index('ix_investigations_metadata', table_name='investigations')

    # Drop the column
    op.drop_column('investigations', 'investigation_metadata')