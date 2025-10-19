# ACAD=GIS Database Schema Guide

**Last Updated**: October 18, 2025  
**Schema Version**: 2.1 (With Test Data)  
**Last Verified**: October 18, 2025

## Database: PostgreSQL + PostGIS + pgvector

**Deployment:**
- Platform: Supabase (free tier)
- PostgreSQL: 15.x
- Extensions: PostGIS ✅, pgvector ✅
- Connection: Session Pooler (IPv4)
- Region: AWS US East 2

**Why PostgreSQL?**
- PostGIS for spatial queries
- pgvector for embeddings (AI)
- JSONB for flexible metadata
- Rock-solid ACID compliance
- Perfect for graph-style relationships

---

## Table Overview

The schema consists of **22 core tables** organized into logical groups:

### Symbol/Block Management (4 tables)
- `block_definitions` - Symbol library ✅ **100 symbols**
- `block_attributes` - Attribute definitions for blocks
- `block_attribute_values` - Attribute values for instances
- `block_inserts` - Symbol placements ✅ **222 placed**

### Layer Management (2 tables)
- `layer_standards` - Standard layer library ✅ **72 layers**
- `layers` - Drawing-specific layer instances

### Drawing/Project Management (3 tables)
- `projects` - Project container ✅ **2 projects**
- `drawings` - DXF files and metadata ✅ **4 drawings**
- `drawing_versions` - Version history

### CAD Standards (5 tables)
- `linetype_standards` - Linetype definitions ✅ **8 types**
- `text_styles` - Text style definitions ✅ **6 styles**
- `dimension_styles` - Dimension styles ✅ **5 styles**
- `hatch_patterns` - Material patterns ✅ **7 patterns**
- `detail_standards` - Construction details ✅ **7 details**

### AI/Semantic Features (3 tables)
- `embeddings` - Centralized embedding storage
- `entity_semantics` - Semantic classifications
- `entity_relationships` - Knowledge graph

### Supporting Tables (5 tables)
- `color_standards` - Color reference ✅ **9 colors**
- `layer_symbol_rules` - Validation rules
- `symbol_formats` - Multiple format storage
- `tags` - Tag definitions
- `entity_tags` - Tag associations

---

## Database Verification

### Current Row Counts (Verified October 18, 2025)

Run this query to verify your database matches documentation:

```sql
SELECT 
  'block_definitions' as table_name, COUNT(*) as count FROM block_definitions
UNION ALL
SELECT 'block_inserts', COUNT(*) FROM block_inserts
UNION ALL
SELECT 'layer_standards', COUNT(*) FROM layer_standards
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'drawings', COUNT(*) FROM drawings
UNION ALL
SELECT 'color_standards', COUNT(*) FROM color_standards
UNION ALL
SELECT 'linetype_standards', COUNT(*) FROM linetype_standards
UNION ALL
SELECT 'text_styles', COUNT(*) FROM text_styles
UNION ALL
SELECT 'dimension_styles', COUNT(*) FROM dimension_styles
UNION ALL
SELECT 'hatch_patterns', COUNT(*) FROM hatch_patterns
UNION ALL
SELECT 'detail_standards', COUNT(*) FROM detail_standards;
```

**Expected Results:**

| Table | Count | Status |
|-------|-------|--------|
| block_definitions | 100 | ✅ Symbol library populated |
| block_inserts | 222 | ✅ Test site fully mapped |
| layer_standards | 72 | ✅ Complete layer library |
| projects | 2 | ✅ Test projects active |
| drawings | 4 | ✅ Multiple test drawings |
| color_standards | 9 | ✅ Color system defined |
| linetype_standards | 8 | ✅ All linetypes loaded |
| text_styles | 6 | ✅ Text styles complete |
| dimension_styles | 5 | ✅ Dimension styles ready |
| hatch_patterns | 7 | ✅ Material patterns set |
| detail_standards | 7 | ✅ Construction details loaded |

### Verify Extensions

```sql
-- Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check PostGIS extension
SELECT * FROM pg_extension WHERE extname = 'postgis';

-- Verify embedding columns exist
SELECT table_name, column_name, udt_name
FROM information_schema.columns 
WHERE column_name LIKE '%embedding%' 
AND table_schema = 'public'
ORDER BY table_name;
```

**Expected embedding columns:**
- `block_definitions.block_embedding` (vector)
- `drawings.drawing_embedding` (vector)
- `layer_standards.layer_embedding` (vector)
- `projects.project_embedding` (vector)

---

## Core Tables

### 1. `block_definitions` (Symbol Library)
**Purpose**: Master library of all CAD symbols

**Current Data**: 100 symbols

```sql
CREATE TABLE public.block_definitions (
    block_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    block_name varchar UNIQUE NOT NULL,
    
    -- Hierarchical parsing
    domain varchar,              -- "utility", "landscape", "site", "traffic", "survey"
    category varchar,            -- "water", "vegetation", "lighting", "sign", etc.
    block_type varchar,
    semantic_type varchar,
    semantic_label varchar,      -- Human-readable name
    
    -- Visual content
    svg_content text NOT NULL,   -- Full SVG file
    svg_viewbox varchar,
    
    -- Placement
    space_type varchar CHECK (space_type IN ('MODEL_SPACE', 'PAPER_SPACE', 'BOTH')),
    base_point_x float DEFAULT 0,
    base_point_y float DEFAULT 0,
    base_point_z float DEFAULT 0,
    
    -- AI/ML fields
    block_embedding vector(1536),
    usage_context text,
    tags text[],
    
    -- Enhanced fields
    is_title_block boolean DEFAULT false,
    is_detail boolean DEFAULT false,
    title_block_size varchar,
    detail_category varchar,
    
    -- Metadata
    description text,
    metadata jsonb,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Symbol Categories (100 total)**:
- **UTILITIES** - Water, Storm Drain, Sewer, Electric, Gas
- **LANDSCAPE** - Trees (Deciduous, Evergreen, Palm), Shrubs
- **SITE** - Lighting, Furniture (Benches, Trash, Bike Racks)
- **TRAFFIC** - Signs (Stop, Yield, Speed, Parking)
- **SURVEY** - Markers, Monuments, Stakes
- **Plus additional symbols** from library ingestion

---

### 2. `block_inserts` (Symbol Placements)
**Purpose**: Track where symbols are placed in drawings

**Current Data**: 222 placements in test site

```sql
CREATE TABLE public.block_inserts (
    insert_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    drawing_id uuid REFERENCES drawings(drawing_id),
    block_id uuid REFERENCES block_definitions(block_id),
    
    -- Position (California State Plane Zone II)
    insert_x double precision NOT NULL,
    insert_y double precision NOT NULL,
    insert_z double precision DEFAULT 0,
    
    -- Transformation
    scale_x double precision DEFAULT 1.0,
    scale_y double precision DEFAULT 1.0,
    rotation double precision DEFAULT 0,
    
    -- Context
    layout_name varchar DEFAULT 'Model',
    space_type varchar DEFAULT 'MODEL_SPACE',
    transformed_geometry geometry,
    
    -- Metadata
    metadata jsonb,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Current Placements (222 total)**:
- 8 Fire hydrants (perimeter coverage)
- 53 Trees (deciduous, evergreen, palm, shrubs)
- 15 Storm drain components
- 12 Water utilities
- 10 Sewer components
- 20 Electrical (poles, transformers, pedestals)
- 8 Gas utilities
- 30 Lighting fixtures
- 25 Site furniture (benches, trash, bikes)
- 20 Traffic signs
- 12 Survey markers
- 9 Additional symbols

---

### 3. `projects` (Project Container)
**Purpose**: Organize drawings into projects

**Current Data**: 2 projects

```sql
CREATE TABLE public.projects (
    project_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_name varchar NOT NULL,
    project_number varchar UNIQUE,
    client_name varchar,
    description text,
    
    -- Coordinate system info
    coordinate_system varchar,
    epsg_code integer,
    coordinate_system_name varchar,
    base_point_x double precision,
    base_point_y double precision,
    base_point_elevation double precision,
    vertical_datum varchar,
    coordinate_notes text,
    
    -- Metadata
    metadata jsonb,
    project_embedding vector(1536),
    tags text[],
    
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Test Projects**:
1. Original test project
2. Santa Rosa test site
   - Location: Santa Rosa, California
   - EPSG: 2226 (CA State Plane Zone II)
   - Base Point: X=6,377,333.0, Y=1,920,867.0
   - Site Size: 467 ft × 467 ft (~5 acres)

---

### 4. `drawings` (DXF Files)
**Purpose**: Store drawing metadata and content

**Current Data**: 4 drawings

```sql
CREATE TABLE public.drawings (
    drawing_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id uuid REFERENCES projects(project_id),
    drawing_name varchar NOT NULL,
    drawing_number varchar,
    description text,
    drawing_type varchar,
    scale varchar,
    
    -- Georeferencing
    file_path varchar,
    file_size bigint,
    drawing_coordinate_system varchar,
    drawing_epsg_code integer,
    cad_units varchar,
    scale_factor double precision DEFAULT 1.0,
    rotation_angle double precision DEFAULT 0.0,
    translation_x double precision DEFAULT 0.0,
    translation_y double precision DEFAULT 0.0,
    is_georeferenced boolean DEFAULT false,
    georeferencing_notes text,
    
    -- Content
    dxf_content text,
    
    -- AI/Version
    drawing_embedding vector(1536),
    current_version integer DEFAULT 1,
    summary text,
    tags text[],
    metadata jsonb,
    
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

---

### 5. `layer_standards` (Layer Library)
**Purpose**: Master library of standard layers

**Current Data**: 72 layer standards

```sql
CREATE TABLE public.layer_standards (
    layer_standard_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    layer_name varchar UNIQUE NOT NULL,
    
    -- Hierarchical naming: DISCIPLINE.CATEGORY.TYPE.STATUS
    discipline varchar NOT NULL,
    category varchar NOT NULL,
    type varchar NOT NULL,
    status varchar NOT NULL CHECK (status IN ('EXISTING', 'PROPOSED', 'DEMO', 'TEMP', 'FOUND', 'SET', 'STANDARD')),
    
    -- Visual properties
    color integer NOT NULL CHECK (color >= 1 AND color <= 255),
    color_rgb varchar,
    linetype varchar DEFAULT 'CONTINUOUS',
    lineweight double precision DEFAULT 0.25,
    is_plottable boolean DEFAULT true,
    is_locked boolean DEFAULT false,
    plot_style varchar,
    transparency integer DEFAULT 0 CHECK (transparency >= 0 AND transparency <= 90),
    
    -- Documentation
    description text,
    usage_context text,
    display_order integer,
    standard_reference varchar DEFAULT 'CUSTOM',
    
    -- AI/ML
    layer_embedding vector(1536),
    tags text[],
    metadata jsonb,
    
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Layer Categories**:
- **CIVIL** layers (boundary, topo, grading, roads, demo)
- **UTILITY** layers (water, sewer, storm - existing and proposed)
- **SITE** layers (buildings, trees, pavement)
- **ANNOTATION** layers (text, dimensions)

---

### 6. `layers` (Drawing Layers)
**Purpose**: Layer instances in specific drawings

```sql
CREATE TABLE public.layers (
    layer_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    drawing_id uuid REFERENCES drawings(drawing_id),
    layer_name varchar NOT NULL,
    layer_standard_id uuid REFERENCES layer_standards(layer_standard_id),
    
    -- Properties (can override standards)
    color integer,
    linetype varchar DEFAULT 'CONTINUOUS',
    lineweight double precision DEFAULT 0.25,
    is_plottable boolean DEFAULT true,
    is_locked boolean DEFAULT false,
    is_frozen boolean DEFAULT false,
    transparency integer DEFAULT 0,
    
    -- Classification
    semantic_category varchar,
    description text,
    usage_context text,
    tags text[],
    
    -- AI
    layer_embedding vector(1536),
    metadata jsonb,
    
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

---

### 7-11. Additional Core Tables

**Attribute Management:**
- `block_attributes` - Attribute definitions for blocks
- `block_attribute_values` - Attribute values for instances

**Version Control:**
- `drawing_versions` - Version history for drawings

**AI/Semantic:**
- `embeddings` - Centralized embedding storage
- `entity_semantics` - Semantic classifications
- `entity_relationships` - Knowledge graph connections

---

## CAD Standards Tables

### 12. `linetype_standards`
**Current Data**: 8 linetypes

```sql
CREATE TABLE public.linetype_standards (
    linetype_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    linetype_name varchar UNIQUE NOT NULL,
    description text,
    pattern text,
    dxf_pattern text,
    scale_factor double precision DEFAULT 1.0,
    usage_context text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Available Linetypes**:
- CONTINUOUS, DASHED, HIDDEN, CENTER, PHANTOM, DOT, FENCELINE, GAS_LINE

---

### 13. `text_styles`
**Current Data**: 6 text styles

```sql
CREATE TABLE public.text_styles (
    style_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    style_name varchar UNIQUE NOT NULL,
    font_name varchar NOT NULL,
    font_file varchar,
    height double precision DEFAULT 0,
    width_factor double precision DEFAULT 1.0,
    oblique_angle double precision DEFAULT 0,
    is_backward boolean DEFAULT false,
    is_upside_down boolean DEFAULT false,
    is_vertical boolean DEFAULT false,
    usage_context text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Available Text Styles**:
- STANDARD (0.12" height, Arial)
- NOTES (0.10" height, Arial)
- TITLES (0.24" height, Arial)
- DIMENSIONS (0.09" height, Arial)
- LABELS (0.08" height, Arial)
- SMALL (0.06" height, Arial)

---

### 14. `dimension_styles`
**Current Data**: 5 dimension styles

```sql
CREATE TABLE public.dimension_styles (
    dimstyle_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    style_name varchar UNIQUE NOT NULL,
    text_style_id uuid REFERENCES text_styles(style_id),
    arrow_type varchar DEFAULT 'CLOSED_FILLED',
    arrow_size double precision DEFAULT 0.18,
    tick_size double precision DEFAULT 0.09,
    text_height double precision DEFAULT 0.12,
    text_gap double precision DEFAULT 0.09,
    text_above_line boolean DEFAULT true,
    text_color integer DEFAULT 7,
    extension_line_offset double precision DEFAULT 0.0625,
    extension_line_extend double precision DEFAULT 0.18,
    dimension_line_color integer DEFAULT 7,
    extension_line_color integer DEFAULT 7,
    overall_scale double precision DEFAULT 1.0,
    usage_context text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Available Dimension Styles**:
- CIVIL_1-20 (scale 20)
- CIVIL_1-40 (scale 40)
- CIVIL_1-50 (scale 50)
- CIVIL_1-100 (scale 100)
- DETAIL_1-1 (scale 1)

---

### 15. `hatch_patterns`
**Current Data**: 7 hatch patterns

```sql
CREATE TABLE public.hatch_patterns (
    hatch_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_name varchar UNIQUE NOT NULL,
    pattern_type varchar NOT NULL,
    angle double precision DEFAULT 0,
    scale double precision DEFAULT 1.0,
    pattern_definition text,
    material_type varchar,
    description text,
    usage_context text,
    svg_preview text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Available Hatch Patterns**:
- ANSI31 (standard crosshatch)
- ANSI32 (steel)
- SOLID (solid fill)
- EARTH (earth material)
- GRAVEL (gravel material)
- CONCRETE (concrete material)
- STEEL (steel material)

---

### 16. `detail_standards`
**Current Data**: 7 construction details

```sql
CREATE TABLE public.detail_standards (
    detail_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    block_id uuid REFERENCES block_definitions(block_id),
    detail_number varchar,
    detail_title varchar NOT NULL,
    detail_category varchar,
    applicable_layers text[],
    applicable_symbols text[],
    scale varchar,
    description text,
    usage_context text,
    typical_application text,
    code_references text[],
    metadata jsonb,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP
);
```

**Available Construction Details**:
- SD-1: Storm Drain Manhole
- SD-2: Storm Drain Inlet
- SD-3: Storm Drain Connection
- WD-1: Water Service Connection
- GD-1: Curb and Gutter Section
- GD-2: Grading Transition Detail
- LD-1: Tree Planting Detail

---

### 17. `color_standards`
**Current Data**: 9 colors

```sql
CREATE TABLE public.color_standards (
    color_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    color_index integer UNIQUE NOT NULL CHECK (color_index >= 1 AND color_index <= 255),
    color_name varchar NOT NULL,
    color_rgb varchar NOT NULL,
    hex_code varchar,
    usage_category varchar,
    description text
);
```

**Color System**:
- **Gray (8)** - EXISTING elements
- **Light Gray (9)** - EXISTING minor elements
- **Yellow (2)** - PROPOSED civil work
- **Magenta (6)** - PROPOSED utility work
- **Green (3)** - PROPOSED site work
- **Red (1)** - DEMOLITION
- **Orange (30)** - TEMPORARY construction
- **Black (7)** - ANNOTATION
- **White (252)** - Background/special use

---

## Supporting Tables

### 18-22. Additional Tables

**Validation & Rules:**
- `layer_symbol_rules` - Layer/symbol validation rules

**Multi-Format Storage:**
- `symbol_formats` - Symbols in multiple formats (SVG, DXF, etc.)

**Tagging System:**
- `tags` - Tag definitions
- `entity_tags` - Tag associations with entities

---

## Key Queries

### Count All Symbols
```sql
SELECT COUNT(*) as total_symbols FROM block_inserts;
-- Returns: 222
```

### Symbols by Type
```sql
SELECT 
    bd.domain,
    bd.category,
    COUNT(*) as count
FROM block_inserts bi
JOIN block_definitions bd ON bi.block_id = bd.block_id
GROUP BY bd.domain, bd.category
ORDER BY bd.domain, count DESC;
```

### Find Symbols Near a Point
```sql
SELECT 
    bd.semantic_label,
    bi.insert_x,
    bi.insert_y,
    SQRT(POWER(bi.insert_x - 6377333.0, 2) + 
         POWER(bi.insert_y - 1920867.0, 2)) as distance_ft
FROM block_inserts bi
JOIN block_definitions bd ON bi.block_id = bd.block_id
WHERE SQRT(POWER(bi.insert_x - 6377333.0, 2) + 
           POWER(bi.insert_y - 1920867.0, 2)) < 100
ORDER BY distance_ft;
```

### Find Similar Symbols (AI)
```sql
SELECT 
    block_name,
    semantic_label,
    1 - (block_embedding <=> %s::vector) as similarity
FROM block_definitions
WHERE block_embedding IS NOT NULL
ORDER BY block_embedding <=> %s::vector
LIMIT 10;
```

### Utilities by Category
```sql
SELECT 
    bd.category,
    COUNT(*) as count
FROM block_inserts bi
JOIN block_definitions bd ON bi.block_id = bd.block_id
WHERE bd.domain = 'utility'
GROUP BY bd.category
ORDER BY count DESC;
```

---

## Current Database State

**Total Tables**: 22  
**Total Symbols Defined**: 100  
**Total Symbols Placed**: 222  
**Total Projects**: 2  
**Total Drawings**: 4  
**Total Layer Standards**: 72  
**Total CAD Standards**: 42

**Test Site Details**:
- Location: Santa Rosa, CA (38.44°N, 122.71°W)
- Coordinate System: EPSG:2226 (CA State Plane Zone II)
- Site Center: X=6,377,333.0, Y=1,920,867.0
- Site Size: 467 ft × 467 ft (~5 acres)
- Complete infrastructure: utilities, landscape, furniture, signs, survey

---

## Why This Schema is AI-Native

1. **Vector Embeddings** - Every major entity supports pgvector embeddings (1536 dimensions)
2. **Hierarchical Names** - Dot-notation enables pattern matching
3. **Graph-Ready** - Relationships table connects everything
4. **Flexible Metadata** - JSONB allows extension without schema changes
5. **Spatial Index** - PostGIS enables "near" queries
6. **Tag Arrays** - Multiple categorizations per entity
7. **Validation Rules** - Machine-readable constraints
8. **Version Control** - Built-in for drawings
9. **Semantic Layer** - AI-generated classifications
10. **Multi-Format** - Symbols in multiple representations
11. **CAD Standards** - Complete standard library
12. **Detail Library** - Construction details linked to symbols

---

## Schema Status

**Platform**: ✅ Supabase free tier  
**Tables**: ✅ 22 core tables deployed  
**Extensions**: ✅ PostGIS, pgvector installed  
**Test Data**: ✅ 222 symbols placed, 4 drawings loaded  

**Data Population**:
- 100 block definitions ✅
- 222 block inserts ✅
- 72 layer standards ✅
- 9 color standards ✅
- 8 linetypes ✅
- 6 text styles ✅
- 5 dimension styles ✅
- 7 hatch patterns ✅
- 7 construction details ✅
- 2 projects ✅
- 4 drawings ✅

**Last Verified**: October 18, 2025

---

## Schema Version History

### Version 2.1 (October 18, 2025) - CURRENT ✅
**Status**: Fully deployed and populated with test data

**Data Added:**
- 100 symbol types across 5 domains
- 222 symbol placements in test site
- 4 test drawings
- Complete infrastructure simulation
- Realistic civil engineering layout

**Tables**: All 22 tables operational

### Version 2.0 (October 17, 2025)
**Added:**
- 5 CAD standards tables
- 4 enhancement columns to block_definitions
- 42 standard records (linetypes, text styles, etc.)

**Status**: All deployed and populated

### Version 1.0 (Initial Deployment)
**Includes:**
- 17 core tables
- Basic symbol library (70 symbols)
- 72 layer standards
- 9 color standards

---

## Health Check Commands

### Verify Table Count
```sql
SELECT COUNT(*) as table_count
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE';
-- Should return: 22
```

### Verify Extensions
```sql
SELECT extname, extversion 
FROM pg_extension 
WHERE extname IN ('postgis', 'vector');
-- Should show both extensions
```

### Check Data Integrity
```sql
-- Verify foreign keys
SELECT COUNT(*) as orphaned_inserts
FROM block_inserts bi
LEFT JOIN block_definitions bd ON bi.block_id = bd.block_id
WHERE bd.block_id IS NULL;
-- Should return: 0

-- Verify embeddings
SELECT 
    COUNT(*) as total_symbols,
    COUNT(block_embedding) as symbols_with_embeddings,
    ROUND(100.0 * COUNT(block_embedding) / COUNT(*), 2) as embedding_coverage_pct
FROM block_definitions;
```

---

*This schema supports traditional SQL queries, modern AI/vector operations, and comprehensive test datasets for system validation.*
