-- Ensure alignments.geom accepts 3D LineStrings
-- Safe to run multiple times

DO $$
BEGIN
  -- Change column type to LineStringZ if not already
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'alignments' AND column_name = 'geom'
  ) THEN
    BEGIN
      ALTER TABLE alignments
      ALTER COLUMN geom TYPE geometry(LineStringZ)
      USING ST_Force3D(geom);
    EXCEPTION WHEN others THEN
      -- ignore if type already compatible
      NULL;
    END;
  END IF;
END$$;

