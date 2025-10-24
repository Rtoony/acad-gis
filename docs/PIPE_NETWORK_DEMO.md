# Pipe Network Demo Guide

Last updated: October 2025

## Overview
Quick reference for the seeded pipe‑network data and tooling added during the slope/analytics push. Use this when demoing the system or when you need to refresh the pipeline before building new features.

## Prerequisites
- FastAPI server running at http://localhost:8000
```bash
uvicorn backend.api_server:app --reload --port 8000
```
- Python virtualenv with the demo dependencies (Streamlit, pandas, pydeck)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip --break-system-packages
python -m pip install streamlit pandas pydeck --break-system-packages
```
- Optional credentials loaded via backend/.env (Supabase session pooler)

## Launch the Tools
1. Pipe Network Editor (frontend HTML)
   - Open tool_launcher.html and click “Pipe Network Editor”.
   - Summary cards (pipe count, below-minimum, average slope, worst margin)
   - Detailed tables for pipes (slope vs required), structures, conflicts, notes
   - Selecting a row fetches GET /api/pipe-networks/{id}/detail

2. Validation Endpoint
   - POST /api/validate/pipe-slope with optional project_id or network_id
   - Response includes summary, results, and per‑pipe slope_margin

3. Streamlit Viewer (interactive map + tables)
```bash
streamlit run tools/pipe_network_viewer.py
```
   - Shows the same slope metrics, structure list, and a PyDeck visualization of each network

## Seeded Demo Data (Supabase)
| Project | Networks | Notes |
|---|---|---|
| Mission Creek Phase 1 | North Basin Storm (original) | Slope checks + violations remain |
| Ridgeview Logistics Park | Ridgeview Storm Phase A, Ridgeview Sanitary Trunk | 3 pipes, 4 structures, 1 violation |
| Harborview Redevelopment | Harborview Storm Retrofit | Biocell connection, smaller pipe |

Extras:
- Utilities (Ridgeview Power, Harborview Gas, Mission Creek Water)
- Conflicts (one per project, tied to utilities)
- Sheet notes seeded for quick reference (Storm Pipe Installation, etc.)

## API Summary
- GET /api/pipe-networks — list with pipe counts + slope stats
- GET /api/pipe-networks/{id}/detail — project info, pipes, structures, conflicts, notes
- POST /api/validate/pipe-slope — aggregated results + summary
- GeoJSON endpoints for pipes/structures filled with the new geometries

## Tips
- The sample data lives in Supabase; rerun the seeding script if you reset the database.
- Streamlit uses localhost:8501. In WSL, open the URL in Windows (Edge/Chrome).
- To disable Streamlit telemetry, create ~/.streamlit/config.toml:
```toml
[browser]
gatherUsageStats = false
```

## Seeding Instructions
- Ensure database env vars are set (prefer backend/.env).
- Run from the repo root:
```bash
python tools/seed_pipe_demo.py
```
- Verify via API:
  - GET /api/pipe-networks returns networks with slope stats
  - GET /api/pipe-networks/{id}/detail shows pipes, structures, conflicts, notes

Idempotency: the script reuses projects/networks by name and refreshes only that network’s pipes/structures. Utilities, conflicts, and notes are upserted by simple keys.

Structure Types
- Some databases enforce allowed structures.type values via a CHECK or enum.
- The seeder auto‑discovers allowed values from the DB (enum labels or parsed from CHECK) and maps MH/CB to the closest match.
- If your schema uses different labels, adjust the synonym lists in tools/seed_pipe_demo.py and rerun.

