-- Seed data for Survey & Civil demo (SRID 2226)
-- Creates a demo project, a few survey points, a utility line, a parcel, and an alignment.

CREATE EXTENSION IF NOT EXISTS postgis;

-- Ensure project exists (insert-if-not-exists pattern)
WITH p AS (
  SELECT project_id FROM projects WHERE project_name = 'Survey Civil Demo'
), ins AS (
  INSERT INTO projects (project_name, project_number, client_name, description)
  SELECT 'Survey Civil Demo', 'SC-DEM', 'Acme Dev', 'Seed data for Survey & Civil module'
  WHERE NOT EXISTS (SELECT 1 FROM p)
  RETURNING project_id
)
SELECT 'ok';

-- Reusable CTE to fetch the project_id regardless of insert above
WITH p AS (
  SELECT project_id FROM projects WHERE project_name = 'Survey Civil Demo' LIMIT 1
)
INSERT INTO survey_points (project_id, point_number, point_type, geometry)
SELECT p.project_id, v.point_number, v.point_type,
       ST_SetSRID(ST_MakePoint(v.easting, v.northing, v.elevation), 2226)
FROM p, (VALUES
  ('CP1','Control',6000000.0000,2000000.0000,100.0000),
  ('TP101','Topo',   6000050.0000,2000025.0000,101.2000),
  ('TP102','Topo',   6000100.0000,2000050.0000,100.8000)
) AS v(point_number, point_type, easting, northing, elevation)
ON CONFLICT (project_id, point_number) DO UPDATE SET
  geometry = EXCLUDED.geometry,
  updated_at = now();

UPDATE survey_points
SET northing = ST_Y(geometry), easting = ST_X(geometry), elevation = ST_Z(geometry)
WHERE project_id = (SELECT project_id FROM projects WHERE project_name = 'Survey Civil Demo');

-- Utility line
WITH p AS (SELECT project_id FROM projects WHERE project_name = 'Survey Civil Demo' LIMIT 1)
INSERT INTO utility_lines (project_id, utility_type, owner, status, diameter, material, geom)
SELECT p.project_id, 'water', 'City', 'existing', '8"', 'PVC',
       ST_SetSRID(ST_GeomFromText('LINESTRING Z (6000000 2000000 100, 6000100 2000100 100)'), 2226)
FROM p
ON CONFLICT DO NOTHING;

-- Parcel polygon (simple square)
WITH p AS (SELECT project_id FROM projects WHERE project_name = 'Survey Civil Demo' LIMIT 1)
INSERT INTO parcels (project_id, apn, owner_name, situs_address, geom, area_sqft)
SELECT p.project_id, '001-001-001', 'Acme Dev', '123 Main St',
       ST_SetSRID(ST_GeomFromText('POLYGON Z ((6000000 2000000 0, 6000200 2000000 0, 6000200 2000200 0, 6000000 2000200 0, 6000000 2000000 0))'), 2226),
       NULL
FROM p
ON CONFLICT DO NOTHING;

UPDATE parcels SET area_sqft = ST_Area(geom)
WHERE project_id = (SELECT project_id FROM projects WHERE project_name = 'Survey Civil Demo');

-- Alignment (3D)
WITH p AS (SELECT project_id FROM projects WHERE project_name = 'Survey Civil Demo' LIMIT 1)
INSERT INTO alignments (project_id, name, design_speed, classification, srid, station_start, geom)
SELECT p.project_id, 'Mainline', 35, 'Local', 2226, 10.0,
       ST_SetSRID(ST_GeomFromText('LINESTRING Z (6000000 2000000 100, 6000250 2000000 101, 6000500 2000100 102)'), 2226)
FROM p
ON CONFLICT DO NOTHING;

SELECT 'seed_survey_civil_demo complete' AS status;

