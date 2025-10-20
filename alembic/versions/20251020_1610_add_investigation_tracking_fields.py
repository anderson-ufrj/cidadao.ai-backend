"""add investigation tracking fields

Revision ID: 77f2e2dbf0ba
Revises: 193da1bb87af
Create Date: 2025-10-20 16:10:54.745619-03:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77f2e2dbf0ba'
down_revision = '193da1bb87af'
branch_labels = None
depends_on = None


def upgrade():
    # Add progress tracking fields
    op.add_column('investigations', sa.Column('progress', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('investigations', sa.Column('current_phase', sa.String(length=100), nullable=True, server_default='pending'))
    op.add_column('investigations', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('investigations', sa.Column('records_processed', sa.Integer(), nullable=True, server_default='0'))


def downgrade():
    # Remove progress tracking fields
    op.drop_column('investigations', 'records_processed')
    op.drop_column('investigations', 'summary')
    op.drop_column('investigations', 'current_phase')
    op.drop_column('investigations', 'progress')
