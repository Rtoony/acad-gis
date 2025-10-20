# Civil Tools Integration Plan

Last Updated: October 2025

## Overview
CivilOS-style, data-first civil tools integrated into ACAD‑GIS. Design data lives in PostgreSQL; drawings/outputs are generated (DXF, LandXML, SVG, JSON, CSV). Frontend tools use React (CDN) with simple tables/forms; Map Viewer consumes GeoJSON.

## Integration Themes
- Data-first: Pipe networks, alignments, BMPs, utilities, conflicts as first-class tables.
- Live validation: Pipe slope minimums, inverts, velocity guardrails; BMP compliance.
- Spatial endpoints: GeoJSON with `bbox`, `srid`, `limit` for performant map fetching.
- Exports: DXF/LandXML/SVG/JSON/CSV directly from DB state.
- Jobs/QA (optional): validations, clash detection, and reports as persisted artifacts.

## Database Extensions (DDL outlines)

```sql
-- Pipe Networks
CREATE TABLE pipe_networks (
  network_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  name text, description text,
  created_at timestamp DEFAULT now()
);

CREATE TABLE structures (
  structure_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  network_id uuid REFERENCES pipe_networks(network_id) ON DELETE CASCADE,
  type text CHECK (type IN ('manhole','inlet','outlet','junction')),
  rim_elev numeric, sump_depth numeric,
  geom geometry(Point, 3857),
  metadata jsonb
);
CREATE INDEX ON structures USING gist (geom);

CREATE TABLE pipes (
  pipe_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  network_id uuid REFERENCES pipe_networks(network_id) ON DELETE CASCADE,
  up_structure_id uuid REFERENCES structures(structure_id) ON DELETE RESTRICT,
  down_structure_id uuid REFERENCES structures(structure_id) ON DELETE RESTRICT,
  diameter_mm numeric, material text, slope numeric, length_m numeric,
  invert_up numeric, invert_dn numeric,
  status text CHECK (status IN ('draft','design','final')),
  geom geometry(LineString, 3857),
  metadata jsonb
);
CREATE INDEX ON pipes USING gist (geom);

-- Alignments
CREATE TABLE alignments (
  alignment_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  name text, design_speed numeric, classification text,
  srid integer,
  geom geometry(LineString),
  station_start numeric
);

CREATE TABLE horizontal_elements (
  element_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  alignment_id uuid REFERENCES alignments(alignment_id) ON DELETE CASCADE,
  type text CHECK (type IN ('tangent','curve','spiral')),
  params jsonb,
  start_station numeric, end_station numeric
);

CREATE TABLE vertical_elements (
  element_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  alignment_id uuid REFERENCES alignments(alignment_id) ON DELETE CASCADE,
  type text CHECK (type IN ('grade','vc_crest','vc_sag')),
  params jsonb,
  start_station numeric, end_station numeric
);

-- BMPs
CREATE TABLE bmps (
  bmp_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  type text,
  area_acres numeric, drainage_area_acres numeric,
  install_date date, status text CHECK (status IN ('active','retired')),
  compliance text CHECK (compliance IN ('good','needs_attention','non_compliant')),
  geom geometry(Geometry, 3857),
  metadata jsonb
);

CREATE TABLE inspections (
  inspection_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  bmp_id uuid REFERENCES bmps(bmp_id) ON DELETE CASCADE,
  date date, findings text, status text CHECK (status IN ('pass','fail')),
  follow_up text
);

CREATE TABLE maintenance_records (
  record_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  bmp_id uuid REFERENCES bmps(bmp_id) ON DELETE CASCADE,
  date date, action text, notes text
);

-- Utilities & Conflicts
CREATE TABLE utilities (
  utility_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  company text, type text, status text,
  request_date date, response_date date, contact text,
  metadata jsonb
);

CREATE TABLE conflicts (
  conflict_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  utility_id uuid REFERENCES utilities(utility_id) ON DELETE SET NULL,
  location geometry(Point, 3857),
  description text, severity text CHECK (severity IN ('low','medium','high')),
  resolved boolean DEFAULT false,
  suggestions text[]
);
CREATE INDEX ON conflicts USING gist (location);

-- Optional: Jobs & Artifacts
CREATE TABLE jobs (
  job_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id uuid REFERENCES projects(project_id) ON DELETE CASCADE,
  type text, status text,
  created_at timestamp DEFAULT now(), completed_at timestamp,
  params jsonb
);

CREATE TABLE artifacts (
  artifact_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  job_id uuid REFERENCES jobs(job_id) ON DELETE CASCADE,
  type text, uri text, metadata jsonb
);
```

SRID Policy: store native SRID where relevant and provide exchange via `srid` param on endpoints; Map tiles likely 3857.

## API Surface (summary)

- CRUD: `/api/pipe-networks`, `/api/pipes`, `/api/structures`, `/api/alignments`, `/api/bmps`, `/api/utilities`, `/api/conflicts`
- Elements: `/api/alignments/{id}/horizontal-elements`, `/api/alignments/{id}/vertical-elements`
- GeoJSON: `/api/pipes/geojson`, `/api/structures/geojson`, `/api/alignments/{id}/geojson`, `/api/bmps/geojson`
- Validation: `/api/validate/pipe-slope`, `/api/validate/velocity`, `/api/clash-detection`
- Exports: `/api/export/dxf|landxml|svg|json|csv`

## Frontend Tools

- Pipe Network Editor, Alignment Editor, BMP Manager, Utility Coordination, Plot & Profile Manager, Sheet Note Manager
- Each as an HTML page under `frontend/tools/`, reusing shared components and API helpers.

## Phasing

- CM‑1: Tables + CRUD + GeoJSON + basic validations + simple UIs
- CM‑2: Map integration + exports + clash detection + artifacts
- CM‑3: Advanced rules, jobs dashboards, solver prototypes


