# Geodesy Policy

## Canonical SRIDs
- EPSG:4326 — canonical storage for exchange/GeoJSON
- EPSG:3857 — for web tiles

## Native SRID
- Retain native SRID per drawing (e.g., EPSG:2226 — CA State Plane Zone 2 ftUS)
- Record unit and conversion factor to meters

## Transform Rules
- Native → 4326 for exchange; 4326 → 3857 for tiles as needed
- For known state plane zones, define proj strings in code (proj4)

## Vertical Datums
- Out of scope initially; record elevation units when present

## Quality
- Validate extents and geometry validity after transform

