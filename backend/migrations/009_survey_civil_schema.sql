-- Survey & Civil Engineering Schema (phase 1)
-- Adds core survey/civil tables per docs. Safe to run multiple times.

-- Coordinate systems lookup (optional, for multi-zone support)
CREATE TABLE IF NOT EXISTS coordinate_systems (
  epsg_code text PRIMARY KEY,
  name text,
  zone integer,
  unit text,
  remarks text
);

-- Project-level defaults for coordinate system
ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS default_epsg_code text DEFAULT 'EPSG:2226',
  ADD COLUMN IF NOT EXISTS default_coordinate_system text DEFAULT 'NAD83 State Plane California Zone 2';

-- Core survey points
CREATE TABLE IF NOT EXISTS survey_points (
  point_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  drawing_id uuid REFERENCES drawings(drawing_id) ON DELETE SET NULL,

  -- Identification
  point_number text NOT NULL,
  point_description text,
  point_code text,
  point_type text, -- Control, Topo, Layout, Benchmark

  -- Geometry (3D State Plane)
  geometry geometry(PointZ, 2226) NOT NULL,
  northing numeric(15,4),
  easting numeric(15,4),
  elevation numeric(10,4),
  coordinate_system text,
  epsg_code text,

  -- Survey metadata
  survey_date date,
  surveyed_by text,
  survey_method text,
  instrument_used text,

  -- Quality
  horizontal_accuracy numeric(8,4),
  vertical_accuracy numeric(8,4),
  accuracy_units text DEFAULT 'Feet',
  quality_code text,

  -- Status
  is_control_point boolean DEFAULT false,
  is_active boolean DEFAULT true,
  superseded_by uuid REFERENCES survey_points(point_id) ON DELETE SET NULL,

  notes text,
  attributes jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE (project_id, point_number)
);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_survey_points_geom'
  ) THEN
    EXECUTE 'CREATE INDEX idx_survey_points_geom ON survey_points USING GIST(geometry)';
  END IF;
END$$;

-- Survey control networks
CREATE TABLE IF NOT EXISTS survey_control_network (
  network_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  name text,
  description text,
  hierarchy text, -- primary/secondary/tertiary
  adjustment_method text, -- Least Squares, Compass Rule, etc.
  standard_errors jsonb,
  confidence_level numeric,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS control_point_membership (
  membership_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  network_id uuid REFERENCES survey_control_network(network_id) ON DELETE CASCADE,
  point_id uuid REFERENCES survey_points(point_id) ON DELETE CASCADE,
  is_fixed boolean DEFAULT false,
  adjusted_geometry geometry(PointZ, 2226),
  residuals jsonb,
  horizontal_accuracy numeric(8,4),
  vertical_accuracy numeric(8,4),
  notes text
);

-- Site features
CREATE TABLE IF NOT EXISTS site_trees (
  tree_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  survey_point_id uuid REFERENCES survey_points(point_id) ON DELETE SET NULL,
  species text,
  dbh_in numeric,
  condition text,
  status text,
  protection_status text,
  notes text
);

CREATE TABLE IF NOT EXISTS utility_structures (
  structure_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  survey_point_id uuid REFERENCES survey_points(point_id) ON DELETE SET NULL,
  structure_type text,
  owner text,
  condition text,
  rim_elev numeric,
  sump_depth numeric,
  ground_elev numeric,
  geom geometry(PointZ, 2226),
  metadata jsonb
);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_utility_structures_geom'
  ) THEN
    EXECUTE 'CREATE INDEX idx_utility_structures_geom ON utility_structures USING GIST(geom)';
  END IF;
END$$;

CREATE TABLE IF NOT EXISTS surface_features (
  feature_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  drawing_id uuid REFERENCES drawings(drawing_id) ON DELETE SET NULL,
  feature_type text,
  material text,
  condition text,
  geom geometry(GeometryZ, 2226),
  metadata jsonb
);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_surface_features_geom'
  ) THEN
    EXECUTE 'CREATE INDEX idx_surface_features_geom ON surface_features USING GIST(geom)';
  END IF;
END$$;

-- Utility networks (engineering representation)
CREATE TABLE IF NOT EXISTS utility_lines (
  line_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  utility_type text, -- water/sewer/storm/electric/gas
  owner text,
  status text,
  diameter text,
  material text,
  geom geometry(LineStringZ, 2226),
  metadata jsonb
);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_utility_lines_geom'
  ) THEN
    EXECUTE 'CREATE INDEX idx_utility_lines_geom ON utility_lines USING GIST(geom)';
  END IF;
END$$;

CREATE TABLE IF NOT EXISTS utility_network_connectivity (
  connectivity_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  line_id uuid REFERENCES utility_lines(line_id) ON DELETE CASCADE,
  node_a uuid,
  node_b uuid,
  connectivity jsonb
);

CREATE TABLE IF NOT EXISTS utility_service_connections (
  service_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  parcel_id uuid,
  line_id uuid REFERENCES utility_lines(line_id) ON DELETE SET NULL,
  structure_id uuid REFERENCES utility_structures(structure_id) ON DELETE SET NULL,
  geom geometry(PointZ, 2226)
);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_utility_service_geom'
  ) THEN
    EXECUTE 'CREATE INDEX idx_utility_service_geom ON utility_service_connections USING GIST(geom)';
  END IF;
END$$;

-- Property & legal
CREATE TABLE IF NOT EXISTS parcels (
  parcel_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  apn text,
  owner_name text,
  situs_address text,
  geom geometry(PolygonZ, 2226),
  area_sqft numeric,
  metadata jsonb
);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_parcels_geom'
  ) THEN
    EXECUTE 'CREATE INDEX idx_parcels_geom ON parcels USING GIST(geom)';
  END IF;
END$$;

CREATE TABLE IF NOT EXISTS parcel_corners (
  corner_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  parcel_id uuid REFERENCES parcels(parcel_id) ON DELETE CASCADE,
  survey_point_id uuid REFERENCES survey_points(point_id) ON DELETE SET NULL,
  corner_type text,
  monument text
);

CREATE TABLE IF NOT EXISTS easements (
  easement_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  easement_type text,
  purpose text,
  geom geometry(GeometryZ, 2226)
);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_easements_geom'
  ) THEN
    EXECUTE 'CREATE INDEX idx_easements_geom ON easements USING GIST(geom)';
  END IF;
END$$;

CREATE TABLE IF NOT EXISTS right_of_way (
  row_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  jurisdiction text,
  geom geometry(GeometryZ, 2226)
);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_row_geom'
  ) THEN
    EXECUTE 'CREATE INDEX idx_row_geom ON right_of_way USING GIST(geom)';
  END IF;
END$$;

-- Survey observations & traverses
CREATE TABLE IF NOT EXISTS survey_observations (
  observation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  session_id text,
  instrument_station_point_id uuid REFERENCES survey_points(point_id) ON DELETE SET NULL,
  backsight_point_id uuid REFERENCES survey_points(point_id) ON DELETE SET NULL,
  target_point_id uuid REFERENCES survey_points(point_id) ON DELETE SET NULL,
  observation_time timestamptz,
  angle_dms text,
  distance_ft numeric,
  method text,
  raw jsonb
);

CREATE TABLE IF NOT EXISTS traverse_loops (
  loop_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  name text,
  closure_ratio text,
  misclosure numeric,
  status text
);

CREATE TABLE IF NOT EXISTS traverse_loop_observations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  loop_id uuid REFERENCES traverse_loops(loop_id) ON DELETE CASCADE,
  observation_id uuid REFERENCES survey_observations(observation_id) ON DELETE CASCADE,
  adjusted boolean,
  residuals jsonb
);

-- Cross sections & earthwork (reference alignments table already exists)
CREATE TABLE IF NOT EXISTS cross_sections (
  section_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  alignment_id uuid REFERENCES alignments(alignment_id) ON DELETE CASCADE,
  station numeric,
  geom geometry(LineStringZ, 2226),
  metadata jsonb
);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_cross_sections_geom'
  ) THEN
    EXECUTE 'CREATE INDEX idx_cross_sections_geom ON cross_sections USING GIST(geom)';
  END IF;
END$$;

CREATE TABLE IF NOT EXISTS cross_section_points (
  point_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  section_id uuid REFERENCES cross_sections(section_id) ON DELETE CASCADE,
  lateral_offset numeric,
  elevation numeric,
  code text
);

CREATE TABLE IF NOT EXISTS earthwork_quantities (
  ew_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  alignment_id uuid REFERENCES alignments(alignment_id) ON DELETE CASCADE,
  station_start numeric,
  station_end numeric,
  cut_cy numeric,
  fill_cy numeric,
  metadata jsonb
);

CREATE TABLE IF NOT EXISTS earthwork_balance (
  balance_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  alignment_id uuid REFERENCES alignments(alignment_id) ON DELETE CASCADE,
  station numeric,
  cumulative_yardage numeric
);

-- Grading & construction
CREATE TABLE IF NOT EXISTS grading_limits (
  grading_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  permit text,
  geom geometry(PolygonZ, 2226),
  area_acres numeric
);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_grading_limits_geom'
  ) THEN
    EXECUTE 'CREATE INDEX idx_grading_limits_geom ON grading_limits USING GIST(geom)';
  END IF;
END$$;

CREATE TABLE IF NOT EXISTS pavement_sections (
  pavement_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  roadway text,
  layers jsonb,
  notes text
);

CREATE TABLE IF NOT EXISTS surface_models (
  surface_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  name text,
  surface_type text,
  bbox geometry(PolygonZ, 2226),
  storage_uri text,
  metadata jsonb
);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_surface_models_bbox'
  ) THEN
    EXECUTE 'CREATE INDEX idx_surface_models_bbox ON surface_models USING GIST(bbox)';
  END IF;
END$$;

CREATE TABLE IF NOT EXISTS typical_sections (
  typical_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text,
  metadata jsonb
);
