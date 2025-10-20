"""merge heads

Revision ID: 193da1bb87af
Revises: 004_investigation_metadata, 007
Create Date: 2025-10-20 16:10:49.587917-03:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '193da1bb87af'
down_revision = ('004_investigation_metadata', '007')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
