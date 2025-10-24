# ACAD-GIS Database Schema (Canonical)

Last Updated: October 2025

Status
- This is the single source of truth for the database schema and data model.
- Supersedes the prior docs/DATABASE_SCHEMA_GUIDE.md (removed).
- Platform: PostgreSQL + PostGIS (optional: pgvector).

Extensions
- Required: uuid-ossp, postgis
- Optional: vector (pgvector) if using embedding columns

Quick Table Index
- Project & Drawings: projects, drawings, drawing_versions, layout_viewports, viewport_standards, drawing_scale_standards, export_jobs
- CAD Standards: layer_standards, linetype_standards, text_styles, dimension_styles, hatch_patterns, color_standards, plot_style_standards
- Symbols & Details: block_definitions, block_attributes, block_attribute_values, block_inserts, detail_standards, symbol_formats
- Drawing Content: drawing_entities, drawing_text, drawing_dimensions, drawing_hatches
- Usage/Validation: drawing_layer_usage, drawing_linetype_usage, layer_symbol_rules, layer_detail_relationships, layer_name_mapping
- AI & Semantics: embeddings, entity_semantics, entity_relationships, fact_graph, tags, entity_tags, glossary_terms
- Civil/Utility: pipe_networks, pipes, structures, utilities, conflicts, bmps, inspections, maintenance_records, alignments, horizontal_elements, vertical_elements, canonical_features
- Materials/Notes/Refs: material_standards, sheet_templates, sheet_notes, standard_notes, code_references
- Backups: abbreviation_standards(_backup), layer_standards_backup, layers_backup, detail_standards_backup

Key Design Decisions
- UUID primary keys on all entities; strong FK relationships for integrity and round‑trip stability
- PostGIS GEOMETRY with Z support for CAD entities; SRID policy: 0 for CAD coordinates, explicit fields for georeferencing
- Model vs Paper in one table using space_type; canonical values: MODEL, PAPER (legacy variants MODEL_SPACE/PAPER_SPACE may appear)
- JSONB metadata columns for DXF carryover and optional attributes; tags as arrays where appropriate
- Standards linkage: instance tables reference standards (layers, hatches, dimensions) to enforce consistency

Verification & Health Checks
- Verify extensions
  SELECT extname, extversion FROM pg_extension WHERE extname IN ('postgis','uuid-ossp','vector');
- Verify table count
  SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';
- Spot‑check row counts
  SELECT 'block_definitions' AS table_name, COUNT(*) FROM block_definitions
  UNION ALL SELECT 'block_inserts', COUNT(*) FROM block_inserts
  UNION ALL SELECT 'layer_standards', COUNT(*) FROM layer_standards
  UNION ALL SELECT 'projects', COUNT(*) FROM projects
  UNION ALL SELECT 'drawings', COUNT(*) FROM drawings
  UNION ALL SELECT 'color_standards', COUNT(*) FROM color_standards
  UNION ALL SELECT 'linetype_standards', COUNT(*) FROM linetype_standards
  UNION ALL SELECT 'text_styles', COUNT(*) FROM text_styles
  UNION ALL SELECT 'dimension_styles', COUNT(*) FROM dimension_styles
  UNION ALL SELECT 'hatch_patterns', COUNT(*) FROM hatch_patterns
  UNION ALL SELECT 'detail_standards', COUNT(*) FROM detail_standards;
- Orphan checks
  SELECT COUNT(*) AS orphaned_inserts
  FROM block_inserts bi LEFT JOIN block_definitions bd ON bi.block_id = bd.block_id
  WHERE bd.block_id IS NULL;
- Embedding coverage (if using pgvector)
  SELECT COUNT(*) AS total, COUNT(block_embedding) AS with_embed,
         ROUND(100.0 * COUNT(block_embedding)/NULLIF(COUNT(*),0),2) AS pct
  FROM block_definitions;

DXF Round‑Trip (Summary)
- Import: Parse DXF → resolve names to FKs → convert geometry → preserve DXF handles/props in JSONB → track usage per drawing
- Export: JOIN through FKs to rebuild names/styles → convert geometry → generate DXF → record metrics in export_jobs

Core Entities (Highlights)
- projects: metadata, coordinate system fields, optional project_embedding, tags
- drawings: file info, georeferencing (epsg, rotations/translations), dxf_content, embeddings, current_version
- layers: per‑drawing layer instances with overrides and optional link to layer_standards
- block_definitions / block_inserts: symbol library and placements with transforms and optional embeddings
- drawing_entities / drawing_text / drawing_dimensions / drawing_hatches: CAD content stored as PostGIS geometries + DXF carryovers
- Civil/Utility: pipe_networks, pipes, structures; utilities + conflicts; BMPs + inspections/maintenance; alignments + horiz/vert elements

Reference DDL Snapshot
- The latest full DDL snapshot has been consolidated from the working schema and is tracked separately to keep this document concise.
- Location: docs/DATABASE_SCHEMA_SNAPSHOT.sql (for reference only; not intended to be executed as‑is)

Schema Status
- Canonical doc maintained alongside migrations; update when schema changes materially
- Prior GUIDE has been removed; this file replaces it

