# ACAD-GIS Development Roadmap (backend-first)

Last Updated: October 2025

## Phase 0 — Environment (Complete)
- WSL Ubuntu 24.04 + Windows Terminal
- Git + GitHub SSH
- Postgres/PostGIS reachable (Supabase)
- Python 3.12 env ready

## Phase 1 — Foundation (Complete)
- Shared CSS/JS, tool launcher, initial tools
- Basic docs and troubleshooting

## Phase 2 — Map Viewer MVP (Complete)
- Selectors for project/drawing
- CRS transform (e.g., EPSG:2226 → EPSG:4326), basemaps
- Geolocation and status bar

## Phase 3 — Database and Pipeline (Current)
Goal: Make the georeferenced DB and DXF pipeline the center of gravity.

1) Schema + Policies
- Canonical geometry tables (points/lines/polygons/labels)
- Units policy: canonical meters; preserve native units + factor
- CRS policy: canonical EPSG:4326 for exchange, EPSG:3857 for tiles; retain native EPSG per drawing

2) DXF Ingest + Normalize
- ezdxf extract primitives/blocks/attributes
- CRS detection, bounds QA, layer and symbol mapping
- Normalize to canonical PostGIS geoms with lineage to drawing

3) Spatial APIs
- GET /api/drawings/{id}/extent
- GET /api/drawings/{id}/geojson?bbox=&srid=&simplify=
- GET /api/layers/{name}/geojson?bbox=&srid=&simplify=&limit=
- Attribute search endpoints with pagination

4) Exports (open formats)
- GeoJSON/GeoPackage first
- Optional MBTiles/PMTiles (vector), SVG/PDF snapshots next

5) Automation/QA
- Validation jobs and reports; lineage tracking for artifacts

## Phase 4 — Python Design Tools (Prototypes)
- Integrate JoshyCAD-style engines (pipe networks, subdivision, grading, profiles)
- Tools read/write DB; produce DXF + optional GeoJSON
- Record tool runs and artifacts in DB (jobs/artifacts tables)

## Phase 5 - Frontend Enhancements (Supporting)
- Map Viewer: layer panel with bbox fetching and identify popups
- Drawing Browser: fast search/filter; link to map extents
- Importer: hook to pipeline jobs and status

## Phase CT - Civil Tools Integration (New)
Goal: Integrate CivilOS-style, data-first civil tools on top of the Phase 3 database and API.

CT-1: Data + CRUD
- Add tables for pipe networks, structures, pipes, alignments (horizontal/vertical), BMPs (with inspections/maintenance), utilities, conflicts, and optional jobs/artifacts.
- CRUD + GeoJSON endpoints for each entity; server-side validations (pipe slopes, BMP compliance).
- Tool pages: Pipe Network Editor, Alignment Editor, BMP Manager, Utility Coordination, Sheet Note Manager, Plot & Profile Manager (basic forms + tables).

CT-2: Spatial + Exports
- Map integration for networks/alignments/BMPs via GeoJSON with bbox/srid.
- Exports: DXF/LandXML/SVG/JSON/CSV for selected scopes (alignment/profile, network, BMPs).
- Clash detection (pipes vs utilities) and validation summaries; persist artifacts.

CT-3: Intelligence
- Velocity/diameter sizing helpers; alignment station equations and vertical curve checks.
- Batch jobs + dashboards (compliance, conflicts, QA).
- Constraint solver and revision intelligence prototypes.




