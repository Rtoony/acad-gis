-- Core tables required by API endpoints and database helpers
-- Safe to run multiple times (IF NOT EXISTS guards). Assumes Postgres 15+.

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "vector";

-- Projects
CREATE TABLE IF NOT EXISTS projects (
  project_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_name text NOT NULL,
  project_number text,
  client_name text,
  description text,
  metadata jsonb,
  created_at timestamptz DEFAULT now()
);

-- Drawings
CREATE TABLE IF NOT EXISTS drawings (
  drawing_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  drawing_name text NOT NULL,
  drawing_number text,
  drawing_type text,
  scale text,
  dxf_content text,
  description text,
  tags text[],
  metadata jsonb,
  drawing_embedding vector(1536),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz
);

-- Layer standards (reference)
CREATE TABLE IF NOT EXISTS layer_standards (
  layer_standard_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  layer_name text UNIQUE NOT NULL,
  description text,
  color integer,
  color_rgb text,
  color_name text,
  display_order integer,
  layer_embedding vector(1536)
);

-- Layers per drawing
CREATE TABLE IF NOT EXISTS layers (
  layer_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  drawing_id uuid NOT NULL REFERENCES drawings(drawing_id) ON DELETE CASCADE,
  layer_name text NOT NULL,
  color integer,
  linetype text,
  lineweight numeric,
  is_plottable boolean,
  is_locked boolean,
  is_frozen boolean,
  layer_standard_id uuid REFERENCES layer_standards(layer_standard_id),
  metadata jsonb,
  UNIQUE (drawing_id, layer_name)
);

-- Block definitions (symbol library)
CREATE TABLE IF NOT EXISTS block_definitions (
  block_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  block_name text UNIQUE NOT NULL,
  svg_content text,
  domain text,
  category text,
  semantic_type text,
  semantic_label text,
  usage_context text,
  tags text[],
  metadata jsonb,
  space_type text,
  block_embedding vector(1536)
);

-- Symbol placements
CREATE TABLE IF NOT EXISTS block_inserts (
  insert_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  drawing_id uuid NOT NULL REFERENCES drawings(drawing_id) ON DELETE CASCADE,
  block_id uuid NOT NULL REFERENCES block_definitions(block_id) ON DELETE RESTRICT,
  insert_x double precision NOT NULL,
  insert_y double precision NOT NULL,
  insert_z double precision,
  scale_x double precision,
  scale_y double precision,
  rotation double precision,
  layout_name text,
  metadata jsonb,
  created_at timestamptz DEFAULT now()
);

-- Pipe networks
CREATE TABLE IF NOT EXISTS pipe_networks (
  network_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  name text,
  description text,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS structures (
  structure_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  network_id uuid REFERENCES pipe_networks(network_id) ON DELETE CASCADE,
  type text,
  rim_elev numeric,
  sump_depth numeric,
  geom geometry(Point, 3857),
  metadata jsonb
);
CREATE INDEX IF NOT EXISTS idx_structures_geom ON structures USING gist (geom);

CREATE TABLE IF NOT EXISTS pipes (
  pipe_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  network_id uuid REFERENCES pipe_networks(network_id) ON DELETE CASCADE,
  up_structure_id uuid REFERENCES structures(structure_id) ON DELETE RESTRICT,
  down_structure_id uuid REFERENCES structures(structure_id) ON DELETE RESTRICT,
  diameter_mm numeric,
  material text,
  slope numeric,
  length_m numeric,
  invert_up numeric,
  invert_dn numeric,
  status text,
  geom geometry(LineString, 3857),
  metadata jsonb
);
CREATE INDEX IF NOT EXISTS idx_pipes_geom ON pipes USING gist (geom);

-- Alignments and elements
CREATE TABLE IF NOT EXISTS alignments (
  alignment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  name text,
  design_speed numeric,
  classification text,
  srid integer,
  geom geometry(LineString),
  station_start numeric
);

CREATE TABLE IF NOT EXISTS horizontal_elements (
  element_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  alignment_id uuid REFERENCES alignments(alignment_id) ON DELETE CASCADE,
  type text,
  params jsonb,
  start_station numeric,
  end_station numeric
);

CREATE TABLE IF NOT EXISTS vertical_elements (
  element_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  alignment_id uuid REFERENCES alignments(alignment_id) ON DELETE CASCADE,
  type text,
  params jsonb,
  start_station numeric,
  end_station numeric
);

-- BMPs and child records
CREATE TABLE IF NOT EXISTS bmps (
  bmp_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  type text,
  area_acres numeric,
  drainage_area_acres numeric,
  install_date date,
  status text,
  compliance text,
  geom geometry(Geometry, 3857),
  metadata jsonb
);

CREATE TABLE IF NOT EXISTS inspections (
  inspection_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bmp_id uuid REFERENCES bmps(bmp_id) ON DELETE CASCADE,
  date date,
  findings text,
  status text,
  follow_up text
);

CREATE TABLE IF NOT EXISTS maintenance_records (
  record_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bmp_id uuid REFERENCES bmps(bmp_id) ON DELETE CASCADE,
  date date,
  action text,
  notes text
);

-- Utilities and conflicts
CREATE TABLE IF NOT EXISTS utilities (
  utility_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  company text,
  type text,
  status text,
  request_date date,
  response_date date,
  contact text,
  metadata jsonb
);

CREATE TABLE IF NOT EXISTS conflicts (
  conflict_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  utility_id uuid REFERENCES utilities(utility_id) ON DELETE SET NULL,
  location geometry(Point, 3857),
  description text,
  severity text,
  resolved boolean DEFAULT false,
  suggestions text[]
);
CREATE INDEX IF NOT EXISTS idx_conflicts_location ON conflicts USING gist (location);

