-- Add variants column to images table
ALTER TABLE images ADD COLUMN IF NOT EXISTS variants JSONB;

-- Optional: Update existing records with a default empty variants object
-- UPDATE images SET variants = '{}'::jsonb WHERE variants IS NULL;

COMMENT ON COLUMN images.variants IS 'JSON object containing URLs for all image variants (original, thumbnail, small, medium, large)';
