-- Seed data for BMPs (and child inspection/maintenance records)
-- Usage: run in a SQL editor connected to your Postgres/PostGIS DB
-- Note: assumes core tables already exist via migrations.

BEGIN;

-- Ensure required extensions (no-op if already installed)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create or reuse a test project
WITH sel AS (
  SELECT project_id FROM projects WHERE project_name = 'Test Civil Project'
), ins AS (
  INSERT INTO projects (project_name, project_number, client_name, description)
  SELECT 'Test Civil Project', 'TP-001', 'Acme Dev', 'Seed data for BMP tests'
  WHERE NOT EXISTS (SELECT 1 FROM sel)
  RETURNING project_id
), p AS (
  SELECT project_id FROM ins
  UNION ALL
  SELECT project_id FROM sel
), sr AS (
  -- Detect target SRID of bmps.geom; 0 means unconstrained
  SELECT NULLIF(Find_SRID('public','bmps','geom'), 0) AS srid_target
)

-- Insert two example BMPs
, b1 AS (
  INSERT INTO bmps (project_id, type, area_acres, drainage_area_acres, install_date, status, compliance, geom, metadata)
  SELECT p.project_id, 'Bioretention', 0.12, 1.8, CURRENT_DATE - INTERVAL '120 days', 'Active', 'good',
         CASE
           WHEN sr.srid_target IS NULL OR sr.srid_target = 3857 THEN
             ST_Buffer(ST_SetSRID(ST_Point(-9735250, 5124450), 3857), 5.0)
           ELSE
             ST_Transform(ST_Buffer(ST_SetSRID(ST_Point(-9735250, 5124450), 3857), 5.0), sr.srid_target)
         END,
         '{"id_label":"BR-1"}'::jsonb
  FROM p CROSS JOIN sr
  RETURNING bmp_id
), b2 AS (
  INSERT INTO bmps (project_id, type, area_acres, drainage_area_acres, install_date, status, compliance, geom, metadata)
  SELECT p.project_id, 'Detention Basin', 0.50, 5.2, CURRENT_DATE - INTERVAL '2 years', 'Needs Maintenance', 'non_compliant',
         CASE
           WHEN sr.srid_target IS NULL OR sr.srid_target = 3857 THEN
             ST_Buffer(ST_SetSRID(ST_Point(-9735150, 5124550), 3857), 5.0)
           ELSE
             ST_Transform(ST_Buffer(ST_SetSRID(ST_Point(-9735150, 5124550), 3857), 5.0), sr.srid_target)
         END,
         '{"id_label":"DB-1"}'::jsonb
  FROM p CROSS JOIN sr
  RETURNING bmp_id
)

-- Child records
, ins_recs AS (
  INSERT INTO inspections (bmp_id, date, findings, status, follow_up)
  SELECT bmp_id, CURRENT_DATE - INTERVAL '15 days', 'Minor sediment accumulation', 'Pass', 'Sweep forebay' FROM b1
  UNION ALL
  SELECT bmp_id, CURRENT_DATE - INTERVAL '180 days', 'Erosion on embankment', 'Fail', 'Repair erosion mat' FROM b2
  RETURNING 1
), mnt_recs AS (
  INSERT INTO maintenance_records (bmp_id, date, action, notes)
  SELECT bmp_id, CURRENT_DATE - INTERVAL '10 days', 'Sediment Removal', 'Vacuum truck' FROM b1
  UNION ALL
  SELECT bmp_id, CURRENT_DATE - INTERVAL '7 days', 'Erosion Repair', 'Added rip-rap' FROM b2
  RETURNING 1
)

SELECT 'bmps_seeded' AS status;

COMMIT;

-- Note: re-running this script will duplicate rows. For idempotent behavior,
-- add WHERE NOT EXISTS conditions tied to project_id and BMP metadata labels.
