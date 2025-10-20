-- ==========================================
-- FIX: Converter coluna ID de UUID para VARCHAR
-- ==========================================

-- Passo 1: Alterar tipo da coluna id de UUID para VARCHAR(255)
ALTER TABLE investigations 
ALTER COLUMN id TYPE VARCHAR(255);

-- Passo 2: Verificar se funcionou
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'investigations' 
AND column_name = 'id';
