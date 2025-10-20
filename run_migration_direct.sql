-- Add progress tracking fields to investigations table
ALTER TABLE investigations ADD COLUMN IF NOT EXISTS progress FLOAT DEFAULT 0.0;
ALTER TABLE investigations ADD COLUMN IF NOT EXISTS current_phase VARCHAR(100) DEFAULT 'pending';
ALTER TABLE investigations ADD COLUMN IF NOT EXISTS summary TEXT;
ALTER TABLE investigations ADD COLUMN IF NOT EXISTS records_processed INTEGER DEFAULT 0;
