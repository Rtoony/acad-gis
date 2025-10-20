# Conversion Pipeline (Open Formats Only)

## Formats
- GeoJSON (interchange, lightweight)
- GeoPackage (bundled, SQL-friendly)
- MBTiles/PMTiles (optional vector/raster tiles for scale)
- SVG/PDF (snapshot/plots)

## Flow
PostGIS → export (OGR / SQL) → write artifacts → record artifact metadata (hash, size, path, srid, units)

## Notes
- Prefer GeoPackage for multi-layer deliverables
- Use simplification and tiling for large layers
- Keep exports reproducible: record query, parameters, and source commit/version

