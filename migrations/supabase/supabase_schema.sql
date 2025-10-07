-- Cidadão.AI - Supabase Database Schema
-- Author: Anderson H. Silva
-- Date: 2025-10-07
-- Description: Complete schema for investigations, anomalies, and audit logs

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE: investigations
-- Stores all investigation records
-- =====================================================
CREATE TABLE IF NOT EXISTS investigations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query TEXT NOT NULL,
    context JSONB DEFAULT '{}'::jsonb,
    initiated_by VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    results JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_investigations_status ON investigations(status);
CREATE INDEX IF NOT EXISTS idx_investigations_created_at ON investigations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_investigations_initiated_by ON investigations(initiated_by);

-- =====================================================
-- TABLE: anomalies
-- Stores detected anomalies from all sources
-- =====================================================
CREATE TABLE IF NOT EXISTS anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    investigation_id UUID REFERENCES investigations(id) ON DELETE CASCADE,
    source VARCHAR(100) NOT NULL, -- 'portal_transparencia', 'katana_scan', etc.
    source_id VARCHAR(255), -- ID from the source system
    anomaly_type VARCHAR(100) NOT NULL, -- 'price_deviation', 'supplier_concentration', etc.
    anomaly_score DECIMAL(5,4) NOT NULL, -- 0.0000 to 1.0000
    severity VARCHAR(50) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    title TEXT NOT NULL,
    description TEXT,
    indicators JSONB DEFAULT '[]'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,
    contract_data JSONB DEFAULT '{}'::jsonb, -- Full contract/dispensa data
    metadata JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) DEFAULT 'detected', -- 'detected', 'investigating', 'confirmed', 'false_positive', 'resolved'
    assigned_to VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for anomalies
CREATE INDEX IF NOT EXISTS idx_anomalies_investigation_id ON anomalies(investigation_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_source ON anomalies(source);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_status ON anomalies(status);
CREATE INDEX IF NOT EXISTS idx_anomalies_score ON anomalies(anomaly_score DESC);
CREATE INDEX IF NOT EXISTS idx_anomalies_created_at ON anomalies(created_at DESC);

-- =====================================================
-- TABLE: audit_logs
-- Comprehensive audit trail
-- =====================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    user_id VARCHAR(255),
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    action VARCHAR(100),
    message TEXT,
    details JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    correlation_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for audit logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_correlation_id ON audit_logs(correlation_id);

-- =====================================================
-- TABLE: alerts
-- Alert notifications for anomalies
-- =====================================================
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    anomaly_id UUID REFERENCES anomalies(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL, -- 'email', 'webhook', 'dashboard'
    severity VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    recipients JSONB DEFAULT '[]'::jsonb, -- Array of email addresses or webhook URLs
    sent_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'failed'
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for alerts
CREATE INDEX IF NOT EXISTS idx_alerts_anomaly_id ON alerts(anomaly_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);

-- =====================================================
-- TABLE: katana_dispensas
-- Cache of Katana API dispensas
-- =====================================================
CREATE TABLE IF NOT EXISTS katana_dispensas (
    id VARCHAR(255) PRIMARY KEY,
    numero VARCHAR(255),
    objeto TEXT,
    valor DECIMAL(15,2),
    fornecedor_nome VARCHAR(500),
    fornecedor_cnpj VARCHAR(20),
    orgao_nome VARCHAR(500),
    orgao_codigo VARCHAR(50),
    data DATE,
    justificativa TEXT,
    raw_data JSONB NOT NULL,
    last_analyzed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for katana_dispensas
CREATE INDEX IF NOT EXISTS idx_katana_dispensas_valor ON katana_dispensas(valor DESC);
CREATE INDEX IF NOT EXISTS idx_katana_dispensas_data ON katana_dispensas(data DESC);
CREATE INDEX IF NOT EXISTS idx_katana_dispensas_fornecedor_cnpj ON katana_dispensas(fornecedor_cnpj);
CREATE INDEX IF NOT EXISTS idx_katana_dispensas_orgao_codigo ON katana_dispensas(orgao_codigo);

-- =====================================================
-- FUNCTIONS: Automatic timestamp updates
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to update updated_at
CREATE TRIGGER update_investigations_updated_at BEFORE UPDATE ON investigations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_anomalies_updated_at BEFORE UPDATE ON anomalies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_katana_dispensas_updated_at BEFORE UPDATE ON katana_dispensas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS: Useful aggregated views
-- =====================================================

-- View: Recent high-severity anomalies
CREATE OR REPLACE VIEW high_severity_anomalies AS
SELECT
    a.id,
    a.title,
    a.anomaly_score,
    a.severity,
    a.source,
    a.status,
    a.created_at,
    i.query as investigation_query,
    i.initiated_by
FROM anomalies a
LEFT JOIN investigations i ON a.investigation_id = i.id
WHERE a.severity IN ('high', 'critical')
    AND a.status != 'false_positive'
ORDER BY a.created_at DESC;

-- View: Anomaly statistics by source
CREATE OR REPLACE VIEW anomaly_stats_by_source AS
SELECT
    source,
    COUNT(*) as total_anomalies,
    AVG(anomaly_score) as avg_score,
    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_count,
    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_count,
    COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as confirmed_count,
    COUNT(CASE WHEN status = 'false_positive' THEN 1 END) as false_positive_count
FROM anomalies
GROUP BY source;

-- View: Investigation summary
CREATE OR REPLACE VIEW investigation_summary AS
SELECT
    i.id,
    i.query,
    i.initiated_by,
    i.status as investigation_status,
    i.created_at,
    i.completed_at,
    COUNT(a.id) as anomalies_count,
    COUNT(CASE WHEN a.severity IN ('high', 'critical') THEN 1 END) as high_severity_count,
    AVG(a.anomaly_score) as avg_anomaly_score
FROM investigations i
LEFT JOIN anomalies a ON i.id = a.investigation_id
GROUP BY i.id, i.query, i.initiated_by, i.status, i.created_at, i.completed_at
ORDER BY i.created_at DESC;

-- =====================================================
-- COMMENTS: Documentation
-- =====================================================
COMMENT ON TABLE investigations IS 'Stores all investigation records from the multi-agent system';
COMMENT ON TABLE anomalies IS 'Detected anomalies from Portal da Transparência and Katana Scan';
COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail for all system actions';
COMMENT ON TABLE alerts IS 'Alert notifications for detected anomalies';
COMMENT ON TABLE katana_dispensas IS 'Cached dispensas de licitação from Katana Scan API';

COMMENT ON COLUMN anomalies.anomaly_score IS 'Confidence score from 0.0000 to 1.0000';
COMMENT ON COLUMN anomalies.severity IS 'Calculated severity: low (0-0.5), medium (0.5-0.7), high (0.7-0.85), critical (0.85-1.0)';
COMMENT ON COLUMN anomalies.status IS 'Lifecycle: detected → investigating → confirmed/false_positive → resolved';
