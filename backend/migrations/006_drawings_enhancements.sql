-- Drawings table enhancements for georeferencing, CAD units, and indexes

-- Add missing columns if not present
ALTER TABLE IF EXISTS drawings
  ADD COLUMN IF NOT EXISTS is_georeferenced boolean DEFAULT false,
  ADD COLUMN IF NOT EXISTS drawing_epsg_code text,
  ADD COLUMN IF NOT EXISTS drawing_coordinate_system text,
  ADD COLUMN IF NOT EXISTS georef_point geometry(PointZ, 4326),
  ADD COLUMN IF NOT EXISTS cad_units text DEFAULT 'Feet',
  ADD COLUMN IF NOT EXISTS scale_factor numeric(10,4) DEFAULT 1.0,
  ADD COLUMN IF NOT EXISTS updated_at timestamptz;

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_drawings_project ON drawings(project_id);
CREATE INDEX IF NOT EXISTS idx_drawings_name ON drawings(drawing_name);
CREATE INDEX IF NOT EXISTS idx_drawings_number ON drawings(drawing_number);
CREATE INDEX IF NOT EXISTS idx_drawings_type ON drawings(drawing_type);
CREATE INDEX IF NOT EXISTS idx_drawings_georeferenced ON drawings(is_georeferenced);
CREATE INDEX IF NOT EXISTS idx_drawings_created ON drawings(created_at DESC);

-- Spatial index for reference point
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = 'idx_drawings_georef_point'
  ) THEN
    EXECUTE 'CREATE INDEX idx_drawings_georef_point ON drawings USING GIST(georef_point)';
  END IF;
END$$;

