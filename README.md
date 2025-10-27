# ACAD-GIS

Open, Python-first CAD/GIS system. The core value is a georeferenced PostGIS database and Python DXF tooling. The UI is a thin, demo-friendly visualization layer to explore what the database knows.

## Vision
- Replace file-bound CAD workflows with a database-backed, GIS-native approach.
- Use only open tools and formats: Python, PostGIS, DXF, GeoJSON, GeoPackage, MBTiles/PMTiles, SVG/PDF.
- Keep the UI lightweight; do real design work with Python “mini-tools” that read/write the DB and emit DXF and metadata.

## Status (Oct 2025)
- Backend: FastAPI running; projects/drawings CRUD; stats/health; drawing render stub; DXF import stub.
- Frontend: Tool launcher; Project Manager; Drawings Manager; Drawing Importer; Map Viewer (selectors, CRS transform, basemaps, geolocation).
- Prototypes: `prototypes/joshycad` contains Python generators demonstrating DXF creation patterns (ezdxf, pandas, numpy, matplotlib).

## Architecture at a Glance
Ingest (DXF) → Normalize (canonical geoms) → Store (PostGIS) → Serve (FastAPI) → Visualize (Leaflet)

See: `docs/ARCHITECTURE.md`, `docs/DXF_PIPELINE.md`, and `docs/API.md`.

## Tech Stack
- Backend: FastAPI, Python 3.12, raw SQL + psycopg2
- Database: PostgreSQL + PostGIS (Supabase)
- Frontend: React 18 (CDN), Leaflet 1.9, Babel Standalone
- Geodesy: proj / pyproj; CRS policy documented in `docs/GEODESY.md`

## Project Structure (high level)
```
acad-gis/
  tool_launcher.html               # Mission Control launcher
  frontend/
    shared/                        # Shared CSS/JS and components
    tools/                         # Mini-tools (HTML + inline React)
  backend/                         # FastAPI + database helpers
  docs/                            # Documentation (see below)
  prototypes/joshycad/             # Python DXF generators (proofs of concept)
  archive/                         # Legacy docs/artifacts
```

## Dev Quick Start
1) Start backend (example)
- Ensure Postgres/PostGIS reachable (Supabase or local)
- Run FastAPI (adjust to your env):
  - `python -m uvicorn backend.api_server:app --reload --port 8000`

2) Open the UI (static HTML)
- Open `tool_launcher.html` directly, or serve `frontend/` via a lightweight server.

3) Configure API base
- Frontend expects `http://localhost:8000/api` by default. Update in `frontend/shared/components.js` if needed.

## New to This Project?
- Start with the beginner-friendly overview: `docs/BEGINNERS_GUIDE.md`

## Secrets and Environment
- Do not commit secrets. Keep `backend/.env` local (it is ignored by Git).
- Follow `docs/DATABASE_CONNECTION.md` for connection details using Supabase Session Pooler.
- Required vars: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.

## GIS Processing (Optional)
- Install QGIS 3.40 LTR (or compatible) on Windows.
- Install required Python packages into the bundled QGIS interpreter:
  - `"C:\Program Files\QGIS 3.40.11\bin\python-qgis-ltr.bat" -m pip install uvicorn fastapi "pydantic>=2,<3" "starlette>=0.37,<0.38" python-dotenv psycopg2-binary python-multipart ezdxf`
- Launch the API with the QGIS-ready helpers:
  - Windows: `start_qgis_server.bat`
  - Linux/WSL: `./start_qgis_server.sh`
- On startup you should see `GIS Processing: ENABLED`. Hit `GET /api/gis/status` to confirm it returns `{ "gis_enabled": true }`.

## Tools
- Project Manager: `frontend/tools/project-manager.html:1`
- Drawings Manager: `frontend/tools/drawings-manager.html:1`
- Drawing Importer: `frontend/tools/drawing-importer.html:1`
- Map Viewer: `frontend/tools/map_viewer.html:1`
- Pipe Network Viewer (Streamlit): `tools/pipe_network_viewer.py`
  - Requires `pip install streamlit pandas pydeck`; run with `streamlit run tools/pipe_network_viewer.py`

## Key Docs
- `docs/ARCHITECTURE.md` — high-level system and data flow
- `docs/DXF_PIPELINE.md` — ingest/normalize pipeline (ezdxf → PostGIS)
- `docs/CONVERSION_PIPELINE.md` - exports to open formats (GeoJSON/GPKG/MBTiles/SVG/PDF)
- `docs/GEODESY.md` - CRS/units policy
- `docs/API.md` - current + planned endpoints
- `docs/DEVELOPMENT_ROADMAP.md` - backend-first milestones
- `docs/CIVIL_TOOLS_PLAN.md` - phased plan for civil-focused tools
- `docs/PIPE_NETWORK_DEMO.md` - how to run the seeded pipe-network demo & viewer
- `docs/PIPE_NETWORK_VALIDATION.md` - **NEW** comprehensive validation for pipe networks (continuity, hydraulic, standards, topology)

## Philosophy
CAD projects are information, not vendor-bound files. Python + PostGIS + open formats can handle the majority of civil/survey workflows without proprietary software.
