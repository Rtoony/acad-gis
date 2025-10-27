-- Seed data for Alignments (and H/V elements)
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
  SELECT 'Test Civil Project', 'TP-001', 'Acme Dev', 'Seed data for Alignment tests'
  WHERE NOT EXISTS (SELECT 1 FROM sel)
  RETURNING project_id
), p AS (
  SELECT project_id FROM ins
  UNION ALL
  SELECT project_id FROM sel
)

-- Insert two example alignments (Web Mercator 3857 geometries)
, sr AS (
  -- Detect target SRID of alignments.geom (0 means unconstrained)
  SELECT NULLIF(Find_SRID('public','alignments','geom'), 0) AS srid_target
), a1 AS (
  INSERT INTO alignments (project_id, name, design_speed, classification, srid, station_start, geom)
  SELECT p.project_id, 'Mainline A', 45, 'Collector', COALESCE(sr.srid_target, 3857), 10.0,
         CASE
           WHEN sr.srid_target IS NULL OR sr.srid_target = 3857 THEN
             ST_SetSRID(ST_GeomFromText('LINESTRING(-9735300 5124300, -9735200 5124400, -9735100 5124500)'), 3857)
           ELSE
             ST_Transform(ST_SetSRID(ST_GeomFromText('LINESTRING(-9735300 5124300, -9735200 5124400, -9735100 5124500)'), 3857), sr.srid_target)
           END
  FROM p CROSS JOIN sr
  RETURNING alignment_id, project_id
), a2 AS (
  INSERT INTO alignments (project_id, name, design_speed, classification, srid, station_start, geom)
  SELECT p.project_id, 'Spur B', 35, 'Local', COALESCE(sr.srid_target, 3857), 0.0,
         CASE
           WHEN sr.srid_target IS NULL OR sr.srid_target = 3857 THEN
             ST_SetSRID(ST_GeomFromText('LINESTRING(-9735100 5124500, -9735000 5124550)'), 3857)
           ELSE
             ST_Transform(ST_SetSRID(ST_GeomFromText('LINESTRING(-9735100 5124500, -9735000 5124550)'), 3857), sr.srid_target)
         END
  FROM p CROSS JOIN sr
  RETURNING alignment_id, project_id
)

-- Horizontal elements for Mainline A
, he AS (
  INSERT INTO horizontal_elements (alignment_id, type, params, start_station, end_station)
  SELECT alignment_id, 'tangent', '{"length_ft": 200}'::jsonb, 10.0, 210.0 FROM a1
  UNION ALL
  SELECT alignment_id, 'curve', '{"radius_ft": 300, "direction": "R"}'::jsonb, 210.0, 510.0 FROM a1
  RETURNING 1
)

-- Vertical elements for Mainline A
, ve AS (
  INSERT INTO vertical_elements (alignment_id, type, params, start_station, end_station)
  SELECT alignment_id, 'grade', '{"slope_pct": 1.5}'::jsonb, 10.0, 260.0 FROM a1
  UNION ALL
  SELECT alignment_id, 'vc_crest', '{"k": 40}'::jsonb, 260.0, 460.0 FROM a1
  RETURNING 1
)

SELECT 'alignments_seeded' AS status;

COMMIT;

-- Note: re-running this script will duplicate rows (no unique constraints on names).
-- For idempotent behavior, add WHERE NOT EXISTS conditions per insert tied to project_id/name.
