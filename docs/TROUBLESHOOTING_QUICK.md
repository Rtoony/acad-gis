# ACAD-GIS Troubleshooting (Quick)

## UI shows blank / duplicate global error
- Symptom: Console shows "Identifier 'ToastManager' has already been declared"
- Fix: Hard refresh (Ctrl+Shift+R) to bust cached scripts; close and reopen the tab if needed.

## API offline in UI
- Ensure FastAPI is running and CORS allows your origin.
- Check `GET /api/health` returns JSON.

## Map not zooming to drawing
- Verify `GET /api/drawings/{id}/render` includes `bounds` and `drawing_epsg_code`.
- If EPSG unknown, viewer falls back to EPSG:4326 assumptions.

## CRS / Units mismatches
- Record native EPSG and units per drawing during ingest.
- See `docs/GEODESY.md` for SRID and unit policy.

## PostGIS connectivity
- Confirm host/port/user/db via environment; avoid committing secrets to docs or repo.
- Test with `psql` or a minimal Python script using the same DSN.

