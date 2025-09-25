"""add ip whitelist table

Revision ID: 006
Revises: 005
Create Date: 2025-01-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ip_whitelists table."""
    op.create_table(
        'ip_whitelists',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('environment', sa.String(20), nullable=False, server_default='production'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=False, server_default='{}'),
        sa.Column('is_cidr', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('cidr_prefix', sa.Integer(), nullable=True),
    )
    
    # Create indexes
    op.create_index(
        'ix_ip_whitelists_ip_address',
        'ip_whitelists',
        ['ip_address']
    )
    
    op.create_index(
        'ix_ip_whitelists_environment',
        'ip_whitelists',
        ['environment']
    )
    
    op.create_index(
        'ix_ip_whitelists_active',
        'ip_whitelists',
        ['active']
    )
    
    op.create_index(
        'ix_ip_whitelists_expires_at',
        'ip_whitelists',
        ['expires_at']
    )
    
    # Create unique constraint on ip + environment
    op.create_unique_constraint(
        'uq_ip_whitelists_ip_environment',
        'ip_whitelists',
        ['ip_address', 'environment']
    )


def downgrade() -> None:
    """Drop ip_whitelists table."""
    op.drop_table('ip_whitelists')