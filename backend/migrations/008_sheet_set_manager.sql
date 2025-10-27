-- Sheet Set Manager schema (idempotent)

CREATE TABLE IF NOT EXISTS project_details (
    project_id UUID PRIMARY KEY REFERENCES projects(project_id) ON DELETE CASCADE,
    project_address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    county VARCHAR(100),
    engineer_of_record VARCHAR(255),
    engineer_license VARCHAR(100),
    jurisdiction VARCHAR(200),
    permit_number VARCHAR(100),
    parcel_number VARCHAR(100),
    project_area_acres DECIMAL(10,2),
    project_description TEXT,
    owner_name VARCHAR(255),
    owner_contact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sheet_category_standards (
    category_code VARCHAR(20) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);
-- Ensure expected columns exist for environments where table pre-exists
ALTER TABLE sheet_category_standards ADD COLUMN IF NOT EXISTS hierarchy_order INTEGER;
ALTER TABLE sheet_category_standards ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE sheet_category_standards ADD COLUMN IF NOT EXISTS discipline VARCHAR(50);
ALTER TABLE sheet_category_standards ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Seed common categories
INSERT INTO sheet_category_standards (category_code, category_name, hierarchy_order, description, discipline, is_active) VALUES
('COVER','Cover Sheets',10,'Project title sheets and general information','General',true),
('DEMO','Demolition Plans',20,'Existing conditions and demolition','Civil',true),
('GRAD','Grading Plans',30,'Site grading and earthwork','Civil',true),
('UTIL','Utility Plans',40,'Water, sewer, storm drainage utilities','Civil',true),
('PAVE','Paving Plans',50,'Street paving and striping','Civil',true),
('LAND','Landscape Plans',60,'Landscape and irrigation','Landscape',true),
('DETAIL','Details',100,'Construction details','Civil',true),
('PROF','Profiles',110,'Utility and street profiles','Civil',true)
ON CONFLICT (category_code) DO NOTHING;

CREATE TABLE IF NOT EXISTS sheet_sets (
    set_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    set_name VARCHAR(255) NOT NULL,
    description TEXT,
    phase VARCHAR(100),
    discipline VARCHAR(50),
    status VARCHAR(50) DEFAULT 'Draft',
    issued_date DATE,
    issued_to VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sheet_sets_project ON sheet_sets(project_id);
CREATE INDEX IF NOT EXISTS idx_sheet_sets_status ON sheet_sets(status);

CREATE TABLE IF NOT EXISTS sheets (
    sheet_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    set_id UUID NOT NULL REFERENCES sheet_sets(set_id) ON DELETE CASCADE,
    sheet_number INTEGER,
    sheet_code VARCHAR(50),
    sheet_title VARCHAR(255) NOT NULL,
    discipline_code VARCHAR(20),
    sheet_type VARCHAR(50),
    sheet_category TEXT,
    sheet_hierarchy_number INTEGER DEFAULT 50,
    scale VARCHAR(50),
    sheet_size VARCHAR(20) DEFAULT '24x36',
    template_id INTEGER,
    revision_number INTEGER DEFAULT 0,
    revision_date DATE,
    notes TEXT,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sheets_set ON sheets(set_id);
CREATE INDEX IF NOT EXISTS idx_sheets_category ON sheets(sheet_category);
CREATE INDEX IF NOT EXISTS idx_sheets_code ON sheets(sheet_code);
DO $$ BEGIN
  CREATE UNIQUE INDEX idx_sheets_unique_code ON sheets(set_id, sheet_code);
EXCEPTION WHEN duplicate_table THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS sheet_drawing_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sheet_id UUID NOT NULL REFERENCES sheets(sheet_id) ON DELETE CASCADE,
    drawing_id UUID REFERENCES drawings(drawing_id) ON DELETE CASCADE,
    layout_name VARCHAR(100),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by VARCHAR(100),
    notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_sheet_drawing_assignments_sheet ON sheet_drawing_assignments(sheet_id);
CREATE INDEX IF NOT EXISTS idx_sheet_drawing_assignments_drawing ON sheet_drawing_assignments(drawing_id);
DO $$ BEGIN
  CREATE UNIQUE INDEX idx_unique_sheet_assignment ON sheet_drawing_assignments(sheet_id, drawing_id, layout_name);
EXCEPTION WHEN duplicate_table THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS sheet_revisions (
    revision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sheet_id UUID NOT NULL REFERENCES sheets(sheet_id) ON DELETE CASCADE,
    revision_number VARCHAR(20) NOT NULL,
    revision_date DATE NOT NULL,
    description TEXT,
    revised_by VARCHAR(100),
    reference_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sheet_revisions_sheet ON sheet_revisions(sheet_id);
CREATE INDEX IF NOT EXISTS idx_sheet_revisions_date ON sheet_revisions(revision_date DESC);

CREATE TABLE IF NOT EXISTS sheet_relationships (
    relationship_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_sheet_id UUID NOT NULL REFERENCES sheets(sheet_id) ON DELETE CASCADE,
    target_sheet_id UUID NOT NULL REFERENCES sheets(sheet_id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sheet_relationships_source ON sheet_relationships(source_sheet_id);
CREATE INDEX IF NOT EXISTS idx_sheet_relationships_target ON sheet_relationships(target_sheet_id);
