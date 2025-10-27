-- Soft delete support for projects

ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS is_archived boolean DEFAULT false,
  ADD COLUMN IF NOT EXISTS archived_at timestamptz;

CREATE INDEX IF NOT EXISTS idx_projects_archived ON projects(is_archived);

