-- Migration: Create investigations table for Cidadão.AI
-- Description: Stores investigation data with complete results for frontend consumption
-- Author: Anderson H. Silva
-- Date: 2025-01-07

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create investigations table
CREATE TABLE IF NOT EXISTS investigations (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- User identification (references auth.users in Supabase)
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),

    -- Investigation details
    query TEXT NOT NULL,
    data_source VARCHAR(100) NOT NULL,

    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    current_phase VARCHAR(100),
    progress DOUBLE PRECISION DEFAULT 0.0,

    -- Results summary
    anomalies_found INTEGER DEFAULT 0,
    total_records_analyzed INTEGER DEFAULT 0,
    confidence_score DOUBLE PRECISION,

    -- JSON data (JSONB for better performance in PostgreSQL)
    filters JSONB DEFAULT '{}'::jsonb,
    anomaly_types JSONB DEFAULT '[]'::jsonb,
    results JSONB DEFAULT '[]'::jsonb,
    investigation_metadata JSONB DEFAULT '{}'::jsonb,

    -- Text fields
    summary TEXT,
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    processing_time_ms INTEGER,

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN (
        'pending', 'processing', 'completed', 'failed', 'cancelled'
    )),
    CONSTRAINT valid_data_source CHECK (data_source IN (
        'contracts', 'expenses', 'agreements', 'biddings', 'servants'
    )),
    CONSTRAINT valid_progress CHECK (progress >= 0.0 AND progress <= 1.0),
    CONSTRAINT valid_confidence CHECK (
        confidence_score IS NULL OR
        (confidence_score >= 0.0 AND confidence_score <= 1.0)
    )
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_investigations_user_id
    ON investigations(user_id);

CREATE INDEX IF NOT EXISTS idx_investigations_status
    ON investigations(status);

CREATE INDEX IF NOT EXISTS idx_investigations_created_at
    ON investigations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_investigations_user_status
    ON investigations(user_id, status);

CREATE INDEX IF NOT EXISTS idx_investigations_session_id
    ON investigations(session_id)
    WHERE session_id IS NOT NULL;

-- Create composite index for common queries
CREATE INDEX IF NOT EXISTS idx_investigations_user_created
    ON investigations(user_id, created_at DESC);

-- Create GIN index for JSONB fields (for efficient queries on JSON data)
CREATE INDEX IF NOT EXISTS idx_investigations_filters
    ON investigations USING GIN (filters);

CREATE INDEX IF NOT EXISTS idx_investigations_results
    ON investigations USING GIN (results);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at on every UPDATE
CREATE TRIGGER update_investigations_updated_at
    BEFORE UPDATE ON investigations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE investigations ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own investigations
CREATE POLICY "Users can view their own investigations"
    ON investigations
    FOR SELECT
    USING (auth.uid() = user_id);

-- RLS Policy: Users can only insert their own investigations
CREATE POLICY "Users can create their own investigations"
    ON investigations
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Users can only update their own investigations
CREATE POLICY "Users can update their own investigations"
    ON investigations
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Users can only delete their own investigations
CREATE POLICY "Users can delete their own investigations"
    ON investigations
    FOR DELETE
    USING (auth.uid() = user_id);

-- Service role bypass (for backend to write with service_role_key)
CREATE POLICY "Service role can manage all investigations"
    ON investigations
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Create view for investigation summaries (lightweight queries)
CREATE OR REPLACE VIEW investigation_summaries AS
SELECT
    id,
    user_id,
    query,
    data_source,
    status,
    progress,
    current_phase,
    anomalies_found,
    total_records_analyzed,
    confidence_score,
    created_at,
    updated_at,
    started_at,
    completed_at,
    processing_time_ms,
    -- Count of results without loading full JSON
    jsonb_array_length(COALESCE(results, '[]'::jsonb)) as results_count
FROM investigations;

-- Grant access to the view
GRANT SELECT ON investigation_summaries TO authenticated;
GRANT SELECT ON investigation_summaries TO service_role;

-- Add helpful comments
COMMENT ON TABLE investigations IS 'Stores investigation data for anomaly detection in government contracts';
COMMENT ON COLUMN investigations.user_id IS 'References auth.users - ensures data isolation per user';
COMMENT ON COLUMN investigations.status IS 'Current status: pending, processing, completed, failed, cancelled';
COMMENT ON COLUMN investigations.progress IS 'Progress percentage from 0.0 to 1.0';
COMMENT ON COLUMN investigations.results IS 'JSONB array of detected anomalies with full details';
COMMENT ON COLUMN investigations.filters IS 'JSONB object with query filters applied';

-- Create function to get investigation statistics
CREATE OR REPLACE FUNCTION get_investigation_stats(p_user_id UUID)
RETURNS TABLE (
    total_investigations BIGINT,
    completed_investigations BIGINT,
    failed_investigations BIGINT,
    pending_investigations BIGINT,
    total_anomalies_found BIGINT,
    avg_confidence_score DOUBLE PRECISION,
    avg_processing_time_ms DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT as total_investigations,
        COUNT(*) FILTER (WHERE status = 'completed')::BIGINT as completed_investigations,
        COUNT(*) FILTER (WHERE status = 'failed')::BIGINT as failed_investigations,
        COUNT(*) FILTER (WHERE status IN ('pending', 'processing'))::BIGINT as pending_investigations,
        COALESCE(SUM(anomalies_found), 0)::BIGINT as total_anomalies_found,
        AVG(confidence_score) as avg_confidence_score,
        AVG(processing_time_ms) as avg_processing_time_ms
    FROM investigations
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execution to authenticated users
GRANT EXECUTE ON FUNCTION get_investigation_stats(UUID) TO authenticated;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE 'Table: investigations';
    RAISE NOTICE 'Indexes: 7 created';
    RAISE NOTICE 'RLS Policies: 5 created';
    RAISE NOTICE 'Views: investigation_summaries';
    RAISE NOTICE 'Functions: get_investigation_stats';
END $$;
