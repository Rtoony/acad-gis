-- Canonical geometry storage for ACAD-GIS
-- Run via backend/run_migrations.py (see script for details)

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS canonical_features (
    feature_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id uuid NOT NULL REFERENCES drawings(drawing_id) ON DELETE CASCADE,
    project_id uuid NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    feature_type text NOT NULL,
    layer_name text,
    native_geom geometry,
    native_srid integer,
    geom geometry,
    metadata jsonb,
    created_at timestamptz DEFAULT now()
);

-- Promote canonical geom column to EPSG:4326 once populated
ALTER TABLE canonical_features
    ALTER COLUMN geom TYPE geometry(Geometry, 4326)
    USING CASE
        WHEN geom IS NULL THEN NULL
        ELSE ST_SetSRID(geom, 4326)
    END;

CREATE INDEX IF NOT EXISTS idx_canonical_features_drawing
    ON canonical_features (drawing_id);

CREATE INDEX IF NOT EXISTS idx_canonical_features_project
    ON canonical_features (project_id);

CREATE INDEX IF NOT EXISTS idx_canonical_features_geom
    ON canonical_features USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_canonical_features_native_geom
    ON canonical_features USING GIST (native_geom);
