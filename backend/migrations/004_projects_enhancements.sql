-- Projects table enhancements: timestamps and indexes
-- Safe to run multiple times

-- Add updated_at column if missing and default to now()
ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT now();

-- Create helpful indexes for common filters/sorts
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(project_name);
CREATE INDEX IF NOT EXISTS idx_projects_client ON projects(client_name);
CREATE INDEX IF NOT EXISTS idx_projects_number ON projects(project_number);
CREATE INDEX IF NOT EXISTS idx_projects_created ON projects(created_at DESC);

