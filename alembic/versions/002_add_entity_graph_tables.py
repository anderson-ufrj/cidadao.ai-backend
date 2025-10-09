"""Add entity graph tables for network analysis

Revision ID: 002_entity_graph
Revises: 001_initial
Create Date: 2025-10-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_entity_graph'
down_revision = '001_initial'  # Update with your actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    # Create entity_nodes table
    op.create_table(
        'entity_nodes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),

        # Entity identification
        sa.Column('entity_type', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(500), nullable=False, index=True),
        sa.Column('normalized_name', sa.String(500), nullable=False, index=True),

        # Official identifiers
        sa.Column('cnpj', sa.String(18), nullable=True, index=True),
        sa.Column('cpf', sa.String(14), nullable=True, index=True),
        sa.Column('agency_code', sa.String(50), nullable=True, index=True),

        # Contact information
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(2), nullable=True),

        # External references
        sa.Column('transparency_portal_url', sa.String(500), nullable=True),
        sa.Column('receita_federal_url', sa.String(500), nullable=True),
        sa.Column('company_website', sa.String(500), nullable=True),

        # Statistics
        sa.Column('total_investigations', sa.Integer(), default=0),
        sa.Column('total_contracts', sa.Integer(), default=0),
        sa.Column('total_contract_value', sa.Float(), default=0.0),
        sa.Column('total_anomalies', sa.Integer(), default=0),

        # Risk scoring
        sa.Column('risk_score', sa.Float(), default=0.0),
        sa.Column('is_sanctioned', sa.Boolean(), default=False),
        sa.Column('sanction_details', sa.JSON(), default={}),

        # Network metrics
        sa.Column('degree_centrality', sa.Float(), default=0.0),
        sa.Column('betweenness_centrality', sa.Float(), default=0.0),
        sa.Column('closeness_centrality', sa.Float(), default=0.0),
        sa.Column('eigenvector_centrality', sa.Float(), default=0.0),

        # Metadata
        sa.Column('first_detected', sa.DateTime(), default=sa.func.now()),
        sa.Column('last_detected', sa.DateTime(), default=sa.func.now()),
        sa.Column('metadata', sa.JSON(), default={}),
    )

    # Create indexes
    op.create_index('idx_entity_type_name', 'entity_nodes', ['entity_type', 'normalized_name'])
    op.create_index('idx_entity_risk', 'entity_nodes', ['risk_score'])

    # Create entity_relationships table
    op.create_table(
        'entity_relationships',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),

        # Relationship endpoints
        sa.Column('source_entity_id', sa.String(36), sa.ForeignKey('entity_nodes.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('target_entity_id', sa.String(36), sa.ForeignKey('entity_nodes.id', ondelete='CASCADE'), nullable=False, index=True),

        # Relationship type
        sa.Column('relationship_type', sa.String(100), nullable=False, index=True),

        # Relationship strength
        sa.Column('strength', sa.Float(), default=1.0),
        sa.Column('confidence', sa.Float(), default=1.0),

        # Evidence
        sa.Column('first_detected', sa.DateTime(), default=sa.func.now()),
        sa.Column('last_detected', sa.DateTime(), default=sa.func.now()),
        sa.Column('detection_count', sa.Integer(), default=1),
        sa.Column('investigation_ids', sa.JSON(), default=[]),
        sa.Column('evidence', sa.JSON(), default={}),

        # Risk flags
        sa.Column('is_suspicious', sa.Boolean(), default=False),
        sa.Column('suspicion_reasons', sa.JSON(), default=[]),

        # Metadata
        sa.Column('metadata', sa.JSON(), default={}),
    )

    # Create indexes
    op.create_index('idx_relationship_source_target', 'entity_relationships', ['source_entity_id', 'target_entity_id'])
    op.create_index('idx_relationship_suspicious', 'entity_relationships', ['is_suspicious'])

    # Create entity_investigation_references table
    op.create_table(
        'entity_investigation_references',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),

        # References
        sa.Column('entity_id', sa.String(36), sa.ForeignKey('entity_nodes.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('investigation_id', sa.String(36), nullable=False, index=True),

        # Context
        sa.Column('role', sa.String(100), nullable=False),
        sa.Column('contract_id', sa.String(100), nullable=True),
        sa.Column('contract_value', sa.Float(), nullable=True),

        # Anomaly involvement
        sa.Column('involved_in_anomalies', sa.Boolean(), default=False),
        sa.Column('anomaly_ids', sa.JSON(), default=[]),

        # Evidence
        sa.Column('evidence_data', sa.JSON(), default={}),

        # Metadata
        sa.Column('detected_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('metadata', sa.JSON(), default={}),
    )

    # Create indexes
    op.create_index('idx_reference_entity_investigation', 'entity_investigation_references', ['entity_id', 'investigation_id'])
    op.create_index('idx_reference_anomalies', 'entity_investigation_references', ['involved_in_anomalies'])

    # Create suspicious_networks table
    op.create_table(
        'suspicious_networks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),

        # Network identification
        sa.Column('network_name', sa.String(255), nullable=False),
        sa.Column('network_type', sa.String(100), nullable=False, index=True),

        # Member entities
        sa.Column('entity_ids', sa.JSON(), default=[]),
        sa.Column('entity_count', sa.Integer(), default=0),

        # Detection details
        sa.Column('detection_reason', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), default=0.0),
        sa.Column('severity', sa.String(50), default='medium'),

        # Investigation references
        sa.Column('investigation_ids', sa.JSON(), default=[]),
        sa.Column('first_detected', sa.DateTime(), default=sa.func.now()),
        sa.Column('last_detected', sa.DateTime(), default=sa.func.now()),

        # Financial impact
        sa.Column('total_contract_value', sa.Float(), default=0.0),
        sa.Column('suspicious_value', sa.Float(), default=0.0),

        # Evidence
        sa.Column('evidence', sa.JSON(), default={}),
        sa.Column('graph_data', sa.JSON(), default={}),

        # Status
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('reviewed', sa.Boolean(), default=False),
        sa.Column('review_notes', sa.Text(), nullable=True),

        # Metadata
        sa.Column('metadata', sa.JSON(), default={}),
    )

    # Create indexes
    op.create_index('idx_network_severity', 'suspicious_networks', ['severity'])
    op.create_index('idx_network_active', 'suspicious_networks', ['is_active'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('suspicious_networks')
    op.drop_table('entity_investigation_references')
    op.drop_table('entity_relationships')
    op.drop_table('entity_nodes')
