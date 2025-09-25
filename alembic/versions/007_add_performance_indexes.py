"""add performance indexes

Revision ID: 007
Revises: 006
Create Date: 2025-01-25
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create performance indexes."""
    
    # Investigations table indexes
    op.create_index(
        'ix_investigations_status_created_at',
        'investigations',
        ['status', 'created_at']
    )
    
    op.create_index(
        'ix_investigations_contract_id',
        'investigations',
        ['contract_id']
    )
    
    # Chat sessions indexes
    op.create_index(
        'ix_chat_sessions_user_id_created_at',
        'chat_sessions',
        ['user_id', 'created_at']
    )
    
    # Chat messages indexes
    op.create_index(
        'ix_chat_messages_session_id_created_at',
        'chat_messages',
        ['session_id', 'created_at']
    )
    
    # API keys indexes (if not already created)
    op.create_index(
        'ix_api_keys_key_hash',
        'api_keys',
        ['key_hash'],
        unique=True,
        postgresql_using='hash'
    )
    
    op.create_index(
        'ix_api_keys_status',
        'api_keys',
        ['status']
    )
    
    # Agents table indexes
    op.create_index(
        'ix_agents_type_status',
        'agents',
        ['type', 'status']
    )
    
    # Anomalies table indexes (if exists)
    try:
        op.create_index(
            'ix_anomalies_investigation_id',
            'anomalies',
            ['investigation_id']
        )
        
        op.create_index(
            'ix_anomalies_severity_created_at',
            'anomalies',
            ['severity', 'created_at']
        )
    except:
        pass  # Table might not exist yet
    
    # Reports table indexes (if exists)
    try:
        op.create_index(
            'ix_reports_investigation_id',
            'reports',
            ['investigation_id']
        )
        
        op.create_index(
            'ix_reports_format_created_at',
            'reports',
            ['format', 'created_at']
        )
    except:
        pass
    
    # Audit logs indexes
    op.create_index(
        'ix_audit_logs_event_type_timestamp',
        'audit_logs',
        ['event_type', 'timestamp']
    )
    
    op.create_index(
        'ix_audit_logs_user_id_timestamp',
        'audit_logs',
        ['user_id', 'timestamp']
    )
    
    # Create partial indexes for better performance
    op.execute("""
        CREATE INDEX CONCURRENTLY ix_investigations_pending 
        ON investigations (created_at) 
        WHERE status = 'PENDING'
    """)
    
    op.execute("""
        CREATE INDEX CONCURRENTLY ix_api_keys_active 
        ON api_keys (created_at) 
        WHERE status = 'ACTIVE'
    """)
    
    # Create GIN index for JSONB columns
    op.execute("""
        CREATE INDEX CONCURRENTLY ix_investigations_results_gin 
        ON investigations USING gin (results)
    """)
    
    op.execute("""
        CREATE INDEX CONCURRENTLY ix_investigations_metadata_gin 
        ON investigations USING gin (metadata)
    """)


def downgrade() -> None:
    """Drop performance indexes."""
    
    # Drop all created indexes
    op.drop_index('ix_investigations_status_created_at', 'investigations')
    op.drop_index('ix_investigations_contract_id', 'investigations')
    op.drop_index('ix_chat_sessions_user_id_created_at', 'chat_sessions')
    op.drop_index('ix_chat_messages_session_id_created_at', 'chat_messages')
    op.drop_index('ix_api_keys_key_hash', 'api_keys')
    op.drop_index('ix_api_keys_status', 'api_keys')
    op.drop_index('ix_agents_type_status', 'agents')
    op.drop_index('ix_audit_logs_event_type_timestamp', 'audit_logs')
    op.drop_index('ix_audit_logs_user_id_timestamp', 'audit_logs')
    
    # Drop partial indexes
    op.execute("DROP INDEX IF EXISTS ix_investigations_pending")
    op.execute("DROP INDEX IF EXISTS ix_api_keys_active")
    
    # Drop GIN indexes
    op.execute("DROP INDEX IF EXISTS ix_investigations_results_gin")
    op.execute("DROP INDEX IF EXISTS ix_investigations_metadata_gin")
    
    # Drop indexes that might not exist
    try:
        op.drop_index('ix_anomalies_investigation_id', 'anomalies')
        op.drop_index('ix_anomalies_severity_created_at', 'anomalies')
        op.drop_index('ix_reports_investigation_id', 'reports')
        op.drop_index('ix_reports_format_created_at', 'reports')
    except:
        pass