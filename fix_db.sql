-- Fix id column type
ALTER TABLE investigations ALTER COLUMN id TYPE VARCHAR(255);

-- Verify the fix
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'investigations' 
AND column_name = 'id';
