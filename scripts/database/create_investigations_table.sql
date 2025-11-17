-- ============================================================================
-- Migration: Create investigations table
-- Revision: 0dba430d74c4
-- Date: 2025-11-17
-- ============================================================================

-- Create investigations table
CREATE TABLE IF NOT EXISTS investigations (
    id VARCHAR(36) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- User identification
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),

    -- Investigation details
    query TEXT NOT NULL,
    data_source VARCHAR(100) NOT NULL,

    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    current_phase VARCHAR(100),
    progress FLOAT DEFAULT 0.0,

    -- Results summary
    anomalies_found INTEGER DEFAULT 0,
    total_records_analyzed INTEGER DEFAULT 0,
    confidence_score FLOAT,

    -- JSON data (PostgreSQL JSONB)
    filters JSONB DEFAULT '{}'::jsonb,
    anomaly_types JSONB DEFAULT '[]'::jsonb,
    results JSONB DEFAULT '[]'::jsonb,
    investigation_metadata JSONB DEFAULT '{}'::jsonb,

    -- Text fields
    summary TEXT,
    error_message TEXT,

    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    processing_time_ms INTEGER
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_investigations_user_id ON investigations(user_id);
CREATE INDEX IF NOT EXISTS idx_investigations_session_id ON investigations(session_id);
CREATE INDEX IF NOT EXISTS idx_investigations_data_source ON investigations(data_source);
CREATE INDEX IF NOT EXISTS idx_investigations_status ON investigations(status);
CREATE INDEX IF NOT EXISTS idx_investigations_user_status ON investigations(user_id, status);
CREATE INDEX IF NOT EXISTS idx_investigations_created_at ON investigations(created_at);

-- Create alembic_version table if it doesn't exist
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Record this migration
INSERT INTO alembic_version (version_num) VALUES ('0dba430d74c4')
ON CONFLICT (version_num) DO NOTHING;

-- Verification queries
SELECT 'Table created successfully!' as status;
SELECT COUNT(*) as investigations_table_exists
FROM information_schema.tables
WHERE table_name = 'investigations';

SELECT COUNT(*) as total_indexes
FROM pg_indexes
WHERE tablename = 'investigations';

SELECT indexname
FROM pg_indexes
WHERE tablename = 'investigations'
ORDER BY indexname;
