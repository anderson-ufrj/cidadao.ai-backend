-- ==========================================
-- RAILWAY DATABASE MIGRATION
-- Adicionar coluna investigation_metadata
-- ==========================================

-- Passo 1: Adicionar a coluna investigation_metadata
ALTER TABLE investigations
ADD COLUMN IF NOT EXISTS investigation_metadata JSONB DEFAULT '{}';

-- Passo 2: Adicionar comentário à coluna
COMMENT ON COLUMN investigations.investigation_metadata IS 'Additional metadata for the investigation';

-- Passo 3: Criar índice GIN para queries eficientes em JSON
CREATE INDEX IF NOT EXISTS ix_investigations_metadata
ON investigations USING gin (investigation_metadata);

-- Verificar se a coluna foi criada com sucesso
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'investigations'
AND column_name = 'investigation_metadata';
