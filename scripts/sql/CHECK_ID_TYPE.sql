-- Verificar tipo atual da coluna id
SELECT column_name, data_type, udt_name
FROM information_schema.columns
WHERE table_name = 'investigations' 
AND column_name = 'id';
