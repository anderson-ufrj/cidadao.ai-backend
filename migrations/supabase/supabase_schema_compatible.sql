-- Supabase Schema for Cidadão.AI 24/7 Auto-Investigation System
-- Compatible with existing investigations table
-- Author: Anderson H. Silva
-- Date: 2025-10-07

-- ============================================
-- PART 1: AUTO INVESTIGATIONS TABLE
-- ============================================
-- This table stores autonomous investigations triggered by Celery tasks
-- Separate from user-initiated investigations

CREATE TABLE IF NOT EXISTS auto_investigations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Investigation details
    query TEXT NOT NULL,
    context JSONB DEFAULT '{}'::jsonb,
    initiated_by VARCHAR(255) NOT NULL, -- e.g., 'auto_investigation_katana', 'auto_investigation_portal'

    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending',

    -- Results
    results JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT valid_auto_investigation_status CHECK (status IN (
        'pending', 'running', 'completed', 'failed', 'cancelled'
    ))
);

-- Indexes for auto_investigations
CREATE INDEX IF NOT EXISTS idx_auto_investigations_status
    ON auto_investigations(status);

CREATE INDEX IF NOT EXISTS idx_auto_investigations_created_at
    ON auto_investigations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_auto_investigations_initiated_by
    ON auto_investigations(initiated_by);

-- Trigger for auto_investigations
CREATE TRIGGER update_auto_investigations_updated_at
    BEFORE UPDATE ON auto_investigations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- PART 2: ANOMALIES TABLE
-- ============================================
-- Stores anomalies detected by agents
-- Can be linked to either user investigations OR auto investigations

CREATE TABLE IF NOT EXISTS anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Link to investigations (either user or auto)
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    auto_investigation_id UUID REFERENCES auto_investigations(id) ON DELETE CASCADE,

    -- Source information
    source VARCHAR(100) NOT NULL, -- e.g., 'katana_scan', 'portal_transparencia', 'manual'
    source_id VARCHAR(255), -- External ID from source system

    -- Anomaly classification
    anomaly_type VARCHAR(100) NOT NULL,
    anomaly_score DECIMAL(5,4) NOT NULL CHECK (anomaly_score >= 0 AND anomaly_score <= 1),
    severity VARCHAR(50) DEFAULT 'medium',

    -- Description
    title TEXT NOT NULL,
    description TEXT,

    -- Details (JSONB for flexibility)
    indicators JSONB DEFAULT '[]'::jsonb, -- List of red flags detected
    recommendations JSONB DEFAULT '[]'::jsonb, -- Suggested actions
    contract_data JSONB DEFAULT '{}'::jsonb, -- Full contract/dispensa data
    metadata JSONB DEFAULT '{}'::jsonb, -- Additional metadata

    -- Status
    status VARCHAR(50) DEFAULT 'detected',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_severity CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_anomaly_status CHECK (status IN (
        'detected', 'under_review', 'confirmed', 'false_positive', 'resolved'
    )),
    -- Must be linked to either investigation_id OR auto_investigation_id (or both)
    CONSTRAINT has_investigation_link CHECK (
        investigation_id IS NOT NULL OR auto_investigation_id IS NOT NULL
    )
);

-- Indexes for anomalies
CREATE INDEX IF NOT EXISTS idx_anomalies_investigation_id
    ON anomalies(investigation_id) WHERE investigation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_anomalies_auto_investigation_id
    ON anomalies(auto_investigation_id) WHERE auto_investigation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_anomalies_severity
    ON anomalies(severity);

CREATE INDEX IF NOT EXISTS idx_anomalies_status
    ON anomalies(status);

CREATE INDEX IF NOT EXISTS idx_anomalies_source
    ON anomalies(source);

CREATE INDEX IF NOT EXISTS idx_anomalies_created_at
    ON anomalies(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_anomalies_score
    ON anomalies(anomaly_score DESC);

-- GIN indexes for JSONB fields
CREATE INDEX IF NOT EXISTS idx_anomalies_contract_data
    ON anomalies USING GIN (contract_data);

CREATE INDEX IF NOT EXISTS idx_anomalies_indicators
    ON anomalies USING GIN (indicators);

-- Trigger for anomalies
CREATE TRIGGER update_anomalies_updated_at
    BEFORE UPDATE ON anomalies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- PART 3: AUDIT LOGS TABLE
-- ============================================
-- Tracks all actions taken by the system

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Event details
    event_type VARCHAR(100) NOT NULL, -- e.g., 'anomaly_detected', 'investigation_started'
    event_source VARCHAR(100) NOT NULL, -- e.g., 'katana_monitor', 'zumbi_agent'

    -- Related entities
    investigation_id UUID REFERENCES investigations(id) ON DELETE SET NULL,
    auto_investigation_id UUID REFERENCES auto_investigations(id) ON DELETE SET NULL,
    anomaly_id UUID REFERENCES anomalies(id) ON DELETE SET NULL,

    -- Event data
    event_data JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for audit_logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type
    ON audit_logs(event_type);

CREATE INDEX IF NOT EXISTS idx_audit_logs_event_source
    ON audit_logs(event_source);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at
    ON audit_logs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_logs_investigation_id
    ON audit_logs(investigation_id) WHERE investigation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_audit_logs_auto_investigation_id
    ON audit_logs(auto_investigation_id) WHERE auto_investigation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_audit_logs_anomaly_id
    ON audit_logs(anomaly_id) WHERE anomaly_id IS NOT NULL;

-- ============================================
-- PART 4: ALERTS TABLE
-- ============================================
-- Tracks alerts sent about anomalies

CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Link to anomaly
    anomaly_id UUID NOT NULL REFERENCES anomalies(id) ON DELETE CASCADE,

    -- Alert details
    alert_type VARCHAR(50) NOT NULL, -- 'email', 'webhook', 'dashboard'
    severity VARCHAR(50) NOT NULL,

    -- Content
    title TEXT NOT NULL,
    message TEXT NOT NULL,

    -- Recipients
    recipients JSONB DEFAULT '[]'::jsonb, -- List of email/webhook URLs

    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_alert_type CHECK (alert_type IN ('email', 'webhook', 'dashboard', 'sms')),
    CONSTRAINT valid_alert_severity CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_alert_status CHECK (status IN ('pending', 'sent', 'failed', 'acknowledged'))
);

-- Indexes for alerts
CREATE INDEX IF NOT EXISTS idx_alerts_anomaly_id
    ON alerts(anomaly_id);

CREATE INDEX IF NOT EXISTS idx_alerts_status
    ON alerts(status);

CREATE INDEX IF NOT EXISTS idx_alerts_alert_type
    ON alerts(alert_type);

CREATE INDEX IF NOT EXISTS idx_alerts_created_at
    ON alerts(created_at DESC);

-- Trigger for alerts
CREATE TRIGGER update_alerts_updated_at
    BEFORE UPDATE ON alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- PART 5: KATANA DISPENSAS CACHE TABLE
-- ============================================
-- Caches dispensas fetched from Katana API

CREATE TABLE IF NOT EXISTS katana_dispensas (
    id VARCHAR(255) PRIMARY KEY,

    -- Basic info
    numero VARCHAR(255),
    objeto TEXT,
    valor DECIMAL(15,2),

    -- Supplier
    fornecedor_nome VARCHAR(500),
    fornecedor_cnpj VARCHAR(20),

    -- Full raw data from Katana API
    raw_data JSONB NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for katana_dispensas
CREATE INDEX IF NOT EXISTS idx_katana_dispensas_numero
    ON katana_dispensas(numero);

CREATE INDEX IF NOT EXISTS idx_katana_dispensas_fornecedor_cnpj
    ON katana_dispensas(fornecedor_cnpj);

CREATE INDEX IF NOT EXISTS idx_katana_dispensas_created_at
    ON katana_dispensas(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_katana_dispensas_valor
    ON katana_dispensas(valor DESC);

-- GIN index for raw_data
CREATE INDEX IF NOT EXISTS idx_katana_dispensas_raw_data
    ON katana_dispensas USING GIN (raw_data);

-- Trigger for katana_dispensas
CREATE TRIGGER update_katana_dispensas_updated_at
    BEFORE UPDATE ON katana_dispensas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- PART 6: VIEWS
-- ============================================

-- High severity anomalies (critical + high)
CREATE OR REPLACE VIEW high_severity_anomalies AS
SELECT
    a.id,
    a.title,
    a.anomaly_score,
    a.severity,
    a.source,
    a.status,
    a.created_at,
    -- Link to either user investigation or auto investigation
    CASE
        WHEN a.investigation_id IS NOT NULL THEN
            (SELECT query FROM investigations WHERE id = a.investigation_id)
        WHEN a.auto_investigation_id IS NOT NULL THEN
            (SELECT query FROM auto_investigations WHERE id = a.auto_investigation_id)
        ELSE 'N/A'
    END as investigation_query,
    CASE
        WHEN a.investigation_id IS NOT NULL THEN 'user_investigation'
        WHEN a.auto_investigation_id IS NOT NULL THEN
            (SELECT initiated_by FROM auto_investigations WHERE id = a.auto_investigation_id)
        ELSE 'unknown'
    END as investigation_source
FROM anomalies a
WHERE a.severity IN ('high', 'critical')
    AND a.status != 'false_positive'
ORDER BY a.created_at DESC;

-- Anomaly statistics by source
CREATE OR REPLACE VIEW anomaly_stats_by_source AS
SELECT
    source,
    COUNT(*) as total_anomalies,
    COUNT(*) FILTER (WHERE severity = 'critical') as critical_count,
    COUNT(*) FILTER (WHERE severity = 'high') as high_count,
    COUNT(*) FILTER (WHERE severity = 'medium') as medium_count,
    COUNT(*) FILTER (WHERE severity = 'low') as low_count,
    AVG(anomaly_score) as avg_score,
    MAX(anomaly_score) as max_score,
    MIN(created_at) as first_detection,
    MAX(created_at) as last_detection
FROM anomalies
WHERE status != 'false_positive'
GROUP BY source
ORDER BY total_anomalies DESC;

-- Auto investigation summary
CREATE OR REPLACE VIEW auto_investigation_summary AS
SELECT
    ai.id,
    ai.query,
    ai.initiated_by,
    ai.status,
    ai.created_at,
    ai.completed_at,
    COUNT(a.id) as anomalies_count,
    COUNT(a.id) FILTER (WHERE a.severity IN ('high', 'critical')) as high_severity_count,
    AVG(a.anomaly_score) as avg_anomaly_score
FROM auto_investigations ai
LEFT JOIN anomalies a ON a.auto_investigation_id = ai.id
GROUP BY ai.id
ORDER BY ai.created_at DESC;

-- ============================================
-- PART 7: RLS POLICIES (if needed)
-- ============================================

-- Enable RLS on new tables
ALTER TABLE auto_investigations ENABLE ROW LEVEL SECURITY;
ALTER TABLE anomalies ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE katana_dispensas ENABLE ROW LEVEL SECURITY;

-- Service role can manage everything (for backend with service_role_key)
CREATE POLICY "Service role can manage auto_investigations"
    ON auto_investigations FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role can manage anomalies"
    ON anomalies FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role can manage audit_logs"
    ON audit_logs FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role can manage alerts"
    ON alerts FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role can manage katana_dispensas"
    ON katana_dispensas FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Authenticated users can view anomalies linked to their investigations
CREATE POLICY "Users can view anomalies from their investigations"
    ON anomalies FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM investigations i
            WHERE i.id = anomalies.investigation_id
            AND i.user_id = auth.uid()
        )
        OR auth.role() = 'service_role'
    );

-- Authenticated users can view alerts for their anomalies
CREATE POLICY "Users can view alerts from their anomalies"
    ON alerts FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM anomalies a
            JOIN investigations i ON i.id = a.investigation_id
            WHERE a.id = alerts.anomaly_id
            AND i.user_id = auth.uid()
        )
        OR auth.role() = 'service_role'
    );

-- ============================================
-- PART 8: HELPER FUNCTIONS
-- ============================================

-- Function to get anomaly statistics
CREATE OR REPLACE FUNCTION get_anomaly_stats(p_days INTEGER DEFAULT 7)
RETURNS TABLE (
    total_anomalies BIGINT,
    critical_anomalies BIGINT,
    high_anomalies BIGINT,
    avg_score DOUBLE PRECISION,
    top_source VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT as total_anomalies,
        COUNT(*) FILTER (WHERE severity = 'critical')::BIGINT as critical_anomalies,
        COUNT(*) FILTER (WHERE severity = 'high')::BIGINT as high_anomalies,
        AVG(anomaly_score) as avg_score,
        (
            SELECT source
            FROM anomalies
            WHERE created_at >= NOW() - (p_days || ' days')::INTERVAL
            GROUP BY source
            ORDER BY COUNT(*) DESC
            LIMIT 1
        ) as top_source
    FROM anomalies
    WHERE created_at >= NOW() - (p_days || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execution
GRANT EXECUTE ON FUNCTION get_anomaly_stats(INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION get_anomaly_stats(INTEGER) TO service_role;

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Cidadão.AI Auto-Investigation Schema Created Successfully!';
    RAISE NOTICE '';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - auto_investigations (autonomous system investigations)';
    RAISE NOTICE '  - anomalies (detected anomalies)';
    RAISE NOTICE '  - audit_logs (system audit trail)';
    RAISE NOTICE '  - alerts (notifications sent)';
    RAISE NOTICE '  - katana_dispensas (Katana API cache)';
    RAISE NOTICE '';
    RAISE NOTICE 'Views created:';
    RAISE NOTICE '  - high_severity_anomalies';
    RAISE NOTICE '  - anomaly_stats_by_source';
    RAISE NOTICE '  - auto_investigation_summary';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Configure Railway environment variables (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)';
    RAISE NOTICE '  2. Test manual triggers: POST /api/v1/tasks/trigger/katana-monitor';
    RAISE NOTICE '  3. Configure alerts: Set ALERT_WEBHOOKS environment variable';
    RAISE NOTICE '  4. Monitor Celery logs for auto-investigation activity';
END $$;
