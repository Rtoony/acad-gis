-- Add invert_elev column to structures table
-- This is critical for pipe network validation and invert continuity checks

ALTER TABLE structures
ADD COLUMN IF NOT EXISTS invert_elev numeric;

COMMENT ON COLUMN structures.invert_elev IS 'Invert elevation at the structure (bottom of incoming/outgoing pipes)';

-- Optionally, you could calculate initial inverts from connected pipes:
-- UPDATE structures s
-- SET invert_elev = (
--     SELECT MIN(LEAST(p.invert_up, p.invert_dn))
--     FROM pipes p
--     WHERE p.up_structure_id = s.structure_id
--        OR p.down_structure_id = s.structure_id
-- )
-- WHERE invert_elev IS NULL;
