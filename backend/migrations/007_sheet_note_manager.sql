-- Sheet Note Manager schema (idempotent)

CREATE TABLE IF NOT EXISTS standard_notes (
    note_id SERIAL PRIMARY KEY,
    note_category VARCHAR(100),
    note_title VARCHAR(255) NOT NULL,
    note_text TEXT NOT NULL,
    discipline VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_standard_notes_category ON standard_notes(note_category);
CREATE INDEX IF NOT EXISTS idx_standard_notes_discipline ON standard_notes(discipline);

CREATE TABLE IF NOT EXISTS sheet_note_sets (
    set_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    set_name VARCHAR(255) NOT NULL,
    description TEXT,
    discipline VARCHAR(50),
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sheet_note_sets_project ON sheet_note_sets(project_id);
CREATE INDEX IF NOT EXISTS idx_sheet_note_sets_active ON sheet_note_sets(project_id, is_active);

CREATE TABLE IF NOT EXISTS project_sheet_notes (
    project_note_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    set_id UUID NOT NULL REFERENCES sheet_note_sets(set_id) ON DELETE CASCADE,
    standard_note_id INTEGER REFERENCES standard_notes(note_id) ON DELETE SET NULL,
    display_code VARCHAR(20),
    custom_title VARCHAR(255),
    custom_text TEXT,
    is_modified BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_project_sheet_notes_set ON project_sheet_notes(set_id);
CREATE INDEX IF NOT EXISTS idx_project_sheet_notes_standard ON project_sheet_notes(standard_note_id);
CREATE INDEX IF NOT EXISTS idx_project_sheet_notes_order ON project_sheet_notes(set_id, sort_order);

CREATE TABLE IF NOT EXISTS sheet_note_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_note_id UUID NOT NULL REFERENCES project_sheet_notes(project_note_id) ON DELETE CASCADE,
    drawing_id UUID NOT NULL REFERENCES drawings(drawing_id) ON DELETE CASCADE,
    layout_name VARCHAR(100) DEFAULT 'Model',
    legend_sequence INTEGER NOT NULL,
    show_in_legend BOOLEAN DEFAULT TRUE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by VARCHAR(100)
);
CREATE INDEX IF NOT EXISTS idx_sheet_note_assignments_note ON sheet_note_assignments(project_note_id);
CREATE INDEX IF NOT EXISTS idx_sheet_note_assignments_drawing ON sheet_note_assignments(drawing_id, layout_name);
CREATE INDEX IF NOT EXISTS idx_sheet_note_assignments_sequence ON sheet_note_assignments(drawing_id, layout_name, legend_sequence);
DO $$ BEGIN
  CREATE UNIQUE INDEX idx_unique_note_assignment ON sheet_note_assignments(project_note_id, drawing_id, layout_name);
EXCEPTION WHEN duplicate_table THEN NULL; END $$;

