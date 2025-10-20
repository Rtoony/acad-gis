# DXF Pipeline

## Goal
Convert DXF drawings into canonical, georeferenced geometries and metadata in PostGIS, without proprietary software.

## Steps
1) Ingest
- Upload DXF → temporary storage
- Parse with `ezdxf` (R2010 target)
- Extract: lines, polylines, arcs, circles, texts, inserts (blocks)

2) Detect CRS and Units
- Read DXF header and metadata; project hints
- If known EPSG (e.g., EPSG:2226), record as native
- Record drawing units and conversion factor to meters

3) Normalize
- Convert to canonical geoms (POINT/LINESTRING/POLYGON) using Shapely
- Transform native → canonical SRID (EPSG:4326)
- Preserve native coordinates/units as metadata on the drawing
- Map layer names to semantic categories

4) Persist
- Insert into PostGIS tables with SRID and attribute columns
- Maintain lineage to project/drawing and source entity id
- Create spatial and attribute indexes

5) QA and Bounds
- Compute extents; validate non-empty geometries
- Record statistics (entity counts by layer/type)

## Tools and Libraries
- ezdxf, shapely, pyproj/proj, psycopg2, GDAL/OGR (for some conversions)

## Outputs
- PostGIS tables populated
- Optional artifacts: GeoJSON and GeoPackage extracts per drawing or layer

