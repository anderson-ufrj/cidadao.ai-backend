-- ============================================================================
-- Cidadão.AI Backend - Railway PostgreSQL Schema
-- Data: 2025-10-16
-- Descrição: Schema completo para persistência de investigações
-- ============================================================================

-- ============================================================================
-- 1. TABELA: investigations
-- ============================================================================
CREATE TABLE IF NOT EXISTS investigations (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),

    -- Query e Configuração
    query TEXT NOT NULL,
    data_source VARCHAR(100) NOT NULL,
    filters JSONB DEFAULT '{}'::jsonb,
    anomaly_types JSONB DEFAULT '[]'::jsonb,

    -- Status e Progresso
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    progress FLOAT DEFAULT 0.0 CHECK (progress >= 0.0 AND progress <= 1.0),
    current_phase VARCHAR(100),

    -- Resultados
    results JSONB,
    summary TEXT,
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    total_records_analyzed INTEGER CHECK (total_records_analyzed >= 0),
    anomalies_found INTEGER CHECK (anomalies_found >= 0),

    -- Erro (se falhar)
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    processing_time_ms INTEGER,

    -- Metadados adicionais
    metadata JSONB DEFAULT '{}'::jsonb
);

-- ============================================================================
-- 2. ÍNDICES PARA PERFORMANCE
-- ============================================================================

-- Índice principal por usuário (queries mais comuns)
CREATE INDEX IF NOT EXISTS idx_investigations_user_id
ON investigations(user_id);

-- Índice por status (para filtrar pending/processing)
CREATE INDEX IF NOT EXISTS idx_investigations_status
ON investigations(status);

-- Índice temporal descendente (investigações recentes)
CREATE INDEX IF NOT EXISTS idx_investigations_created_at
ON investigations(created_at DESC);

-- Índice por sessão (quando existir)
CREATE INDEX IF NOT EXISTS idx_investigations_session_id
ON investigations(session_id)
WHERE session_id IS NOT NULL;

-- Índice composto para queries complexas
CREATE INDEX IF NOT EXISTS idx_investigations_user_status_created
ON investigations(user_id, status, created_at DESC);

-- Índice GIN para busca JSONB em filters
CREATE INDEX IF NOT EXISTS idx_investigations_filters_gin
ON investigations USING GIN (filters);

-- Índice GIN para busca JSONB em results
CREATE INDEX IF NOT EXISTS idx_investigations_results_gin
ON investigations USING GIN (results);

-- ============================================================================
-- 3. TRIGGER PARA ATUALIZAR updated_at AUTOMATICAMENTE
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_investigations_updated_at ON investigations;
CREATE TRIGGER update_investigations_updated_at
    BEFORE UPDATE ON investigations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 4. TRIGGER PARA CALCULAR processing_time_ms AUTOMATICAMENTE
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_processing_time()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL THEN
        NEW.processing_time_ms = EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at)) * 1000;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS calculate_investigation_processing_time ON investigations;
CREATE TRIGGER calculate_investigation_processing_time
    BEFORE UPDATE OF completed_at ON investigations
    FOR EACH ROW
    EXECUTE FUNCTION calculate_processing_time();

-- ============================================================================
-- 5. COMENTÁRIOS PARA DOCUMENTAÇÃO
-- ============================================================================

COMMENT ON TABLE investigations IS 'Investigações de transparência pública com resultados de anomalias detectadas';

COMMENT ON COLUMN investigations.id IS 'UUID único da investigação';
COMMENT ON COLUMN investigations.user_id IS 'ID do usuário que criou a investigação';
COMMENT ON COLUMN investigations.session_id IS 'ID da sessão de chat (opcional)';
COMMENT ON COLUMN investigations.query IS 'Query original do usuário';
COMMENT ON COLUMN investigations.data_source IS 'Fonte de dados: contracts, suppliers, agencies, etc';
COMMENT ON COLUMN investigations.filters IS 'Filtros JSON aplicados: CNPJ, datas, órgãos, etc';
COMMENT ON COLUMN investigations.anomaly_types IS 'Tipos de anomalias a detectar: price_deviation, concentration, etc';
COMMENT ON COLUMN investigations.status IS 'Status: pending, processing, completed, failed, cancelled';
COMMENT ON COLUMN investigations.progress IS 'Progresso 0.0 a 1.0 (0% a 100%)';
COMMENT ON COLUMN investigations.current_phase IS 'Fase atual: data_retrieval, anomaly_detection, analysis, etc';
COMMENT ON COLUMN investigations.results IS 'Array JSONB de anomalias detectadas com detalhes completos';
COMMENT ON COLUMN investigations.summary IS 'Resumo executivo da investigação em texto';
COMMENT ON COLUMN investigations.confidence_score IS 'Score de confiança médio (0.0 a 1.0)';
COMMENT ON COLUMN investigations.total_records_analyzed IS 'Total de registros analisados';
COMMENT ON COLUMN investigations.anomalies_found IS 'Total de anomalias detectadas';
COMMENT ON COLUMN investigations.error_message IS 'Mensagem de erro se status = failed';
COMMENT ON COLUMN investigations.processing_time_ms IS 'Tempo de processamento em milissegundos (calculado automaticamente)';
COMMENT ON COLUMN investigations.metadata IS 'Metadados adicionais em JSONB';

-- ============================================================================
-- 6. QUERIES DE VERIFICAÇÃO
-- ============================================================================

-- Verificar tabela criada
SELECT
    table_name,
    table_type
FROM information_schema.tables
WHERE table_name = 'investigations';

-- Verificar colunas
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'investigations'
ORDER BY ordinal_position;

-- Verificar índices
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'investigations';

-- Verificar triggers
SELECT
    trigger_name,
    event_manipulation,
    event_object_table
FROM information_schema.triggers
WHERE event_object_table = 'investigations';

-- ============================================================================
-- 7. DADOS DE EXEMPLO (OPCIONAL - para testes)
-- ============================================================================

-- Inserir investigação de teste
-- INSERT INTO investigations (
--     user_id,
--     query,
--     data_source,
--     status,
--     filters
-- ) VALUES (
--     'test-user-001',
--     'Teste de persistência PostgreSQL Railway',
--     'contracts',
--     'pending',
--     '{"year": 2023, "state": "SP"}'::jsonb
-- );

-- ============================================================================
-- FIM DO SCHEMA
-- ============================================================================

-- Exibir mensagem de sucesso
DO $$
BEGIN
    RAISE NOTICE '✅ Schema PostgreSQL criado com sucesso!';
    RAISE NOTICE '📊 Tabela: investigations';
    RAISE NOTICE '📈 Índices: 7 índices criados';
    RAISE NOTICE '⚙️  Triggers: 2 triggers criados';
END $$;
