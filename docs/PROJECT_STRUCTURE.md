# ACAD-GIS Project Structure

## Top-level
```
acad-gis/
  tool_launcher.html
  backend/
  frontend/
    shared/
    tools/
  docs/
  prototypes/
    joshycad/
  archive/
```

## Frontend
`frontend/shared/` contains shared styles and utilities used by all mini-tools.
- `styles.css` — Mission Control theme
- `components.js` — API helpers and utilities
- `react-components.js` — reusable React UI (DataTable, Modal, Header, etc.)
- `api.js`, `state.js`, `dev-tools.js` — enhanced helpers

`frontend/tools/` contains single-file HTML tools (React via CDN + Babel):
- `project-manager.html`, `drawing_browser.html`, `drawing-importer.html`, `map_viewer.html`

## Backend
- `backend/api_server_ENHANCED.py` — FastAPI app and endpoints
- `backend/database.py` — DB helpers
- Import scripts and tests under `backend/`

## Prototypes
`prototypes/joshycad/` — Python DXF generators and helpers (proofs of concept):
- `cad_generator.py`, `subdivision.py`, `grading_3d.py`, `block_library.py`, etc.

## Docs
Key references:
- `docs/ARCHITECTURE.md` — high-level system and data flow
- `docs/DXF_PIPELINE.md` — ingest/normalize pipeline
- `docs/GEODESY.md` — CRS and units policy
- `docs/API.md` — endpoints
- `docs/DEVELOPMENT_ROADMAP.md` — milestones

## Notes
- The UI is intentionally thin and demo-oriented; the core focus is the database + Python DXF tooling.

