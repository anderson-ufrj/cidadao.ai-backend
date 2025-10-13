"""Add performance indexes for common queries

Revision ID: 003_performance_indexes
Revises: 002_add_audit_tables
Create Date: 2025-01-19

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = "003_performance_indexes"
down_revision = "002_entity_graph"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes for common query patterns."""

    # Investigations table indexes
    op.create_index(
        "idx_investigations_user_status_created",
        "investigations",
        ["user_id", "status", sa.text("created_at DESC")],
        postgresql_concurrently=True,
        if_not_exists=True,
    )

    op.create_index(
        "idx_investigations_status_created",
        "investigations",
        ["status", sa.text("created_at DESC")],
        postgresql_concurrently=True,
        if_not_exists=True,
    )

    # Partial index for active investigations
    op.create_index(
        "idx_investigations_active",
        "investigations",
        ["id", "user_id"],
        postgresql_where=sa.text("status IN ('pending', 'processing')"),
        postgresql_concurrently=True,
        if_not_exists=True,
    )

    # Contracts table indexes (if exists)
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_org_year
        ON contracts(orgao_id, ano, valor DESC);
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_fornecedor
        ON contracts(fornecedor_id, created_at DESC);
    """
    )

    # Full-text search index for contracts
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contracts_search
        ON contracts USING gin(to_tsvector('portuguese', coalesce(objeto, '') || ' ' || coalesce(descricao, '')));
    """
    )

    # Anomalies table indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_anomalies_type_severity
        ON anomalies(type, severity DESC, created_at DESC);
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_anomalies_investigation
        ON anomalies(investigation_id, confidence_score DESC);
    """
    )

    # Agent messages table indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_messages_investigation
        ON agent_messages(investigation_id, created_at);
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_messages_agent_type
        ON agent_messages(agent_type, status, created_at DESC);
    """
    )

    # Chat sessions indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chat_sessions_user_active
        ON chat_sessions(user_id, updated_at DESC)
        WHERE active = true;
    """
    )

    # Memory entries indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_memory_entries_type_importance
        ON memory_entries(memory_type, importance DESC, created_at DESC);
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_memory_entries_embedding
        ON memory_entries USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """
    )

    # Audit logs indexes
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_time
        ON audit_logs(user_id, created_at DESC);
    """
    )

    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_event_severity
        ON audit_logs(event_type, severity, created_at DESC);
    """
    )

    # API request logs (for performance monitoring)
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_logs_endpoint_time
        ON api_request_logs(endpoint, response_time_ms)
        WHERE created_at > CURRENT_DATE - INTERVAL '7 days';
    """
    )

    # Update table statistics
    op.execute("ANALYZE investigations;")
    op.execute("ANALYZE contracts;")
    op.execute("ANALYZE anomalies;")
    op.execute("ANALYZE agent_messages;")


def downgrade() -> None:
    """Remove performance indexes."""

    # Drop investigations indexes
    op.drop_index(
        "idx_investigations_user_status_created", "investigations", if_exists=True
    )
    op.drop_index("idx_investigations_status_created", "investigations", if_exists=True)
    op.drop_index("idx_investigations_active", "investigations", if_exists=True)

    # Drop other indexes
    op.execute("DROP INDEX IF EXISTS idx_contracts_org_year;")
    op.execute("DROP INDEX IF EXISTS idx_contracts_fornecedor;")
    op.execute("DROP INDEX IF EXISTS idx_contracts_search;")
    op.execute("DROP INDEX IF EXISTS idx_anomalies_type_severity;")
    op.execute("DROP INDEX IF EXISTS idx_anomalies_investigation;")
    op.execute("DROP INDEX IF EXISTS idx_agent_messages_investigation;")
    op.execute("DROP INDEX IF EXISTS idx_agent_messages_agent_type;")
    op.execute("DROP INDEX IF EXISTS idx_chat_sessions_user_active;")
    op.execute("DROP INDEX IF EXISTS idx_memory_entries_type_importance;")
    op.execute("DROP INDEX IF EXISTS idx_memory_entries_embedding;")
    op.execute("DROP INDEX IF EXISTS idx_audit_logs_user_time;")
    op.execute("DROP INDEX IF EXISTS idx_audit_logs_event_severity;")
    op.execute("DROP INDEX IF EXISTS idx_api_logs_endpoint_time;")
