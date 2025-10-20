"""
Database connection and query helpers for ACAD=GIS.
Handles all PostgreSQL + pgvector operations.
"""

import os
import json
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from contextlib import contextmanager
import uuid

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Database configuration - loads from .env file
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'sslmode': 'prefer',  # More forgiving than 'require'
    'connect_timeout': 10,
    'keepalives': 1,
    'keepalives_idle': 30,
    'keepalives_interval': 10,
    'keepalives_count': 5
}

# Validate required environment variables
required_vars = ['DB_HOST', 'DB_PASSWORD']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise Exception(
        f"Missing required environment variables: {', '.join(missing_vars)}\n"
        f"Please create a .env file with these variables or set them in your environment."
    )


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_query(query: str, params: tuple = None, fetch: bool = True) -> List[Dict]:
    """Execute a SQL query and return results."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                return [dict(row) for row in cur.fetchall()]
            return []

def execute_single(query: str, params: tuple = None) -> Optional[Dict]:
    """Execute a SQL query and return single result."""
    results = execute_query(query, params, fetch=True)
    return results[0] if results else None

# ============================================
# BLOCK DEFINITIONS (SYMBOLS)
# ============================================

def create_block_definition(
    block_name: str,
    svg_content: str,
    domain: str = None,
    category: str = None,
    semantic_type: str = None,
    semantic_label: str = None,
    usage_context: str = None,
    tags: List[str] = None,
    metadata: Dict = None
) -> str:
    """Create a new block definition (symbol)."""
    
    block_id = str(uuid.uuid4())
    
    query = """
        INSERT INTO block_definitions (
            block_id, block_name, svg_content, domain, category,
            semantic_type, semantic_label, usage_context, tags, metadata,
            space_type
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (block_name) DO UPDATE SET
            svg_content = EXCLUDED.svg_content,
            domain = EXCLUDED.domain,
            category = EXCLUDED.category,
            semantic_type = EXCLUDED.semantic_type,
            semantic_label = EXCLUDED.semantic_label,
            usage_context = EXCLUDED.usage_context,
            tags = EXCLUDED.tags,
            metadata = EXCLUDED.metadata
        RETURNING block_id
    """
    
    result = execute_single(query, (
        block_id, block_name, svg_content, domain, category,
        semantic_type, semantic_label, usage_context, tags,
        Json(metadata) if metadata else None, 'BOTH'
    ))
    
    return result['block_id']

def get_block_definition(block_name: str) -> Optional[Dict]:
    """Get block definition by name."""
    query = "SELECT * FROM block_definitions WHERE block_name = %s"
    return execute_single(query, (block_name,))

def get_all_blocks() -> List[Dict]:
    """Get all block definitions."""
    return execute_query("SELECT * FROM block_definitions ORDER BY block_name")

# ============================================
# DRAWINGS
# ============================================

def create_drawing(
    project_id: str,
    drawing_name: str,
    drawing_number: str = None,
    drawing_type: str = None,
    scale: str = None,
    dxf_content: str = None,
    description: str = None,
    tags: List[str] = None,
    metadata: Dict = None
) -> str:
    """Create a new drawing record."""
    
    drawing_id = str(uuid.uuid4())
    
    query = """
        INSERT INTO drawings (
            drawing_id, project_id, drawing_name, drawing_number,
            drawing_type, scale, dxf_content, description, tags, metadata
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING drawing_id
    """
    
    result = execute_single(query, (
        drawing_id, project_id, drawing_name, drawing_number,
        drawing_type, scale, dxf_content, description, tags,
        Json(metadata) if metadata else None
    ))
    
    return result['drawing_id']

def get_drawing(drawing_id: str) -> Optional[Dict]:
    """Get drawing by ID."""
    query = "SELECT * FROM drawings WHERE drawing_id = %s"
    return execute_single(query, (drawing_id,))

def update_drawing_dxf(drawing_id: str, dxf_content: str):
    """Update the DXF content of a drawing."""
    query = """
        UPDATE drawings 
        SET dxf_content = %s, updated_at = CURRENT_TIMESTAMP
        WHERE drawing_id = %s
    """
    execute_query(query, (dxf_content, drawing_id), fetch=False)

# ============================================
# LAYERS
# ============================================

def create_layer(
    drawing_id: str,
    layer_name: str,
    color: int = None,
    linetype: str = 'CONTINUOUS',
    lineweight: float = 0.25,
    is_plottable: bool = True,
    is_locked: bool = False,
    is_frozen: bool = False,
    layer_standard_id: str = None
) -> str:
    """Create a layer for a specific drawing."""
    
    layer_id = str(uuid.uuid4())
    
    # Try to find matching layer standard
    if not layer_standard_id:
        standard = execute_single(
            "SELECT layer_standard_id FROM layer_standards WHERE layer_name = %s",
            (layer_name,)
        )
        if standard:
            layer_standard_id = standard['layer_standard_id']
    
    query = """
        INSERT INTO layers (
            layer_id, drawing_id, layer_name, color, linetype, lineweight,
            is_plottable, is_locked, is_frozen, layer_standard_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (drawing_id, layer_name) DO UPDATE SET
            color = EXCLUDED.color,
            linetype = EXCLUDED.linetype,
            lineweight = EXCLUDED.lineweight
        RETURNING layer_id
    """
    
    result = execute_single(query, (
        layer_id, drawing_id, layer_name, color, linetype, lineweight,
        is_plottable, is_locked, is_frozen, layer_standard_id
    ))
    
    return result['layer_id']

def get_layers(drawing_id: str) -> List[Dict]:
    """Get all layers for a drawing."""
    query = "SELECT * FROM layers WHERE drawing_id = %s ORDER BY layer_name"
    return execute_query(query, (drawing_id,))

# ============================================
# BLOCK INSERTS (SYMBOL PLACEMENTS)
# ============================================

def create_block_insert(
    drawing_id: str,
    block_name: str,
    insert_x: float,
    insert_y: float,
    insert_z: float = 0,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    rotation: float = 0,
    layer_name: str = '0',
    metadata: Dict = None
) -> str:
    """Create a block insert (symbol placement)."""
    
    insert_id = str(uuid.uuid4())
    
    # Get block_id from block_name
    block = get_block_definition(block_name)
    if not block:
        raise ValueError(f"Block definition '{block_name}' not found")
    
    block_id = block['block_id']
    
    query = """
        INSERT INTO block_inserts (
            insert_id, drawing_id, block_id, insert_x, insert_y, insert_z,
            scale_x, scale_y, rotation, layout_name, metadata
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING insert_id
    """
    
    result = execute_single(query, (
        insert_id, drawing_id, block_id, insert_x, insert_y, insert_z,
        scale_x, scale_y, rotation, 'Model',
        Json(metadata) if metadata else None
    ))
    
    return result['insert_id']

def get_block_inserts(drawing_id: str) -> List[Dict]:
    """Get all block inserts for a drawing."""
    query = """
        SELECT 
            bi.*,
            bd.block_name,
            bd.domain,
            bd.category
        FROM block_inserts bi
        JOIN block_definitions bd ON bi.block_id = bd.block_id
        WHERE bi.drawing_id = %s
        ORDER BY bi.created_at
    """
    return execute_query(query, (drawing_id,))

# ============================================
# LAYER STANDARDS
# ============================================

def get_layer_standard(layer_name: str) -> Optional[Dict]:
    """Get layer standard by name."""
    query = "SELECT * FROM layer_standards WHERE layer_name = %s"
    return execute_single(query, (layer_name,))

def get_all_layer_standards() -> List[Dict]:
    """Get all layer standards."""
    return execute_query(
        "SELECT * FROM layer_standards ORDER BY display_order, layer_name"
    )

# ============================================
# PROJECTS
# ============================================

def create_project(
    project_name: str,
    project_number: str = None,
    client_name: str = None,
    description: str = None,
    metadata: Dict = None
) -> str:
    """Create a new project."""
    
    project_id = str(uuid.uuid4())
    
    query = """
        INSERT INTO projects (
            project_id, project_name, project_number, client_name,
            description, metadata
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING project_id
    """
    
    result = execute_single(query, (
        project_id, project_name, project_number, client_name,
        description, Json(metadata) if metadata else None
    ))
    
    return result['project_id']

def get_project(project_id: str) -> Optional[Dict]:
    """Get project by ID."""
    query = "SELECT * FROM projects WHERE project_id = %s"
    return execute_single(query, (project_id,))

# ============================================
# EMBEDDINGS
# ============================================

def update_block_embedding(block_id: str, embedding: List[float]):
    """Update block embedding vector."""
    query = """
        UPDATE block_definitions 
        SET block_embedding = %s
        WHERE block_id = %s
    """
    execute_query(query, (embedding, block_id), fetch=False)

def update_layer_embedding(layer_standard_id: str, embedding: List[float]):
    """Update layer standard embedding vector."""
    query = """
        UPDATE layer_standards 
        SET layer_embedding = %s
        WHERE layer_standard_id = %s
    """
    execute_query(query, (embedding, layer_standard_id), fetch=False)

def update_drawing_embedding(drawing_id: str, embedding: List[float]):
    """Update drawing embedding vector."""
    query = """
        UPDATE drawings 
        SET drawing_embedding = %s
        WHERE drawing_id = %s
    """
    execute_query(query, (embedding, drawing_id), fetch=False)

# ============================================
# SEMANTIC SEARCH
# ============================================

def vector_search(
    table: str,
    embedding_column: str,
    query_embedding: List[float],
    limit: int = 10
) -> List[Dict]:
    """
    Perform vector similarity search.
    
    Args:
        table: 'block_definitions', 'layer_standards', or 'drawings'
        embedding_column: 'block_embedding', 'layer_embedding', or 'drawing_embedding'
        query_embedding: Vector to search for
        limit: Number of results
    """
    
    id_column = {
        'block_definitions': 'block_id',
        'layer_standards': 'layer_standard_id',
        'drawings': 'drawing_id'
    }[table]
    
    name_column = {
        'block_definitions': 'block_name',
        'layer_standards': 'layer_name',
        'drawings': 'drawing_name'
    }[table]
    
    query = f"""
        SELECT 
            {id_column},
            {name_column},
            1 - ({embedding_column} <=> %s::vector) as similarity
        FROM {table}
        WHERE {embedding_column} IS NOT NULL
        ORDER BY {embedding_column} <=> %s::vector
        LIMIT %s
    """
    
    return execute_query(query, (query_embedding, query_embedding, limit))

# ============================================
# CIVIL TOOLS STUB HELPERS
# ============================================

def _json_or_none(value: Any):
    return Json(value) if value is not None else None


def _build_geom_clause(geom: Any, srid: Optional[int] = None, default_srid: int = 3857):
    """Return SQL fragment and params to insert/update a geometry column."""
    if geom in (None, ""):
        return "NULL", []

    if srid is None:
        srid = default_srid

    if isinstance(geom, (dict, list)):
        geom_str = json.dumps(geom)
        return "ST_SetSRID(ST_GeomFromGeoJSON(%s), %s)", [geom_str, srid]

    geom_str = str(geom).strip()
    if not geom_str:
        return "NULL", []
    if geom_str.startswith('{') or geom_str.startswith('['):
        return "ST_SetSRID(ST_GeomFromGeoJSON(%s), %s)", [geom_str, srid]
    return "ST_SetSRID(ST_GeomFromText(%s), %s)", [geom_str, srid]


def _derive_project_id_from_network(network_id: Optional[str]) -> Optional[str]:
    if not network_id:
        return None
    network = execute_single(
        "SELECT project_id FROM pipe_networks WHERE network_id = %s",
        (network_id,)
    )
    return network['project_id'] if network else None


def _execute_update(table: str, pk_column: str, record_id: str, assignments: List[str], params: List[Any]) -> bool:
    if not assignments:
        return False
    params = params + [record_id]
    query = f"UPDATE {table} SET {', '.join(assignments)} WHERE {pk_column} = %s"
    execute_query(query, tuple(params), fetch=False)
    return True

def list_pipe_networks(project_id: Optional[str] = None) -> List[Dict]:
    """Return pipe networks with counts."""
    where = ""
    params: List[Any] = []
    if project_id:
        where = "WHERE pn.project_id = %s"
        params.append(project_id)

    query = f"""
        SELECT
            pn.network_id,
            pn.project_id,
            proj.project_name,
            pn.name,
            pn.description,
            pn.created_at,
            COUNT(p.pipe_id) AS pipe_count
        FROM pipe_networks pn
        LEFT JOIN projects proj ON pn.project_id = proj.project_id
        LEFT JOIN pipes p ON p.network_id = pn.network_id
        {where}
        GROUP BY pn.network_id, pn.project_id, proj.project_name, pn.name, pn.description, pn.created_at
        ORDER BY pn.created_at DESC NULLS LAST, pn.name
    """
    return execute_query(query, tuple(params) if params else None)

def list_structures(network_id: Optional[str] = None, project_id: Optional[str] = None) -> List[Dict]:
    """Return structures with optional filters."""
    filters = []
    params: List[Any] = []
    if network_id:
        filters.append("s.network_id = %s")
        params.append(network_id)
    if project_id:
        filters.append("s.project_id = %s")
        params.append(project_id)

    where = f"WHERE {' AND '.join(filters)}" if filters else ""

    query = f"""
        SELECT
            s.structure_id,
            s.project_id,
            proj.project_name,
            s.network_id,
            pn.name AS network_name,
            s.type,
            s.rim_elev,
            s.sump_depth,
            ST_AsGeoJSON(s.geom) AS geom,
            s.metadata
        FROM structures s
        LEFT JOIN pipe_networks pn ON s.network_id = pn.network_id
        LEFT JOIN projects proj ON s.project_id = proj.project_id
        {where}
        ORDER BY COALESCE(s.rim_elev, 0) DESC, s.structure_id
    """
    return execute_query(query, tuple(params) if params else None)

def list_pipes(network_id: Optional[str] = None) -> List[Dict]:
    """Return pipes with optional network filter."""
    where = ""
    params: List[Any] = []
    if network_id:
        where = "WHERE p.network_id = %s"
        params.append(network_id)

    query = f"""
        SELECT
            p.pipe_id,
            p.network_id,
            pn.name AS network_name,
            p.up_structure_id,
            p.down_structure_id,
            p.diameter_mm,
            p.material,
            p.slope,
            p.length_m,
            p.invert_up,
            p.invert_dn,
            p.status,
            ST_AsGeoJSON(p.geom) AS geom,
            p.metadata
        FROM pipes p
        LEFT JOIN pipe_networks pn ON p.network_id = pn.network_id
        {where}
        ORDER BY p.diameter_mm DESC NULLS LAST, p.pipe_id
    """
    return execute_query(query, tuple(params) if params else None)

def list_alignments(project_id: Optional[str] = None) -> List[Dict]:
    """Return alignments with optional project filter."""
    where = ""
    params: List[Any] = []
    if project_id:
        where = "WHERE a.project_id = %s"
        params.append(project_id)

    query = f"""
        SELECT
            a.alignment_id,
            a.project_id,
            proj.project_name,
            a.name,
            a.design_speed,
            a.classification,
            a.srid,
            a.station_start,
            ST_AsGeoJSON(a.geom) AS geom,
            COALESCE(he.count, 0) AS horizontal_elements,
            COALESCE(ve.count, 0) AS vertical_elements
        FROM alignments a
        LEFT JOIN projects proj ON a.project_id = proj.project_id
        LEFT JOIN (
            SELECT alignment_id, COUNT(*) AS count
            FROM horizontal_elements
            GROUP BY alignment_id
        ) he ON he.alignment_id = a.alignment_id
        LEFT JOIN (
            SELECT alignment_id, COUNT(*) AS count
            FROM vertical_elements
            GROUP BY alignment_id
        ) ve ON ve.alignment_id = a.alignment_id
        {where}
        ORDER BY a.name
    """
    return execute_query(query, tuple(params) if params else None)

def list_horizontal_elements(alignment_id: str) -> List[Dict]:
    query = """
        SELECT element_id, alignment_id, type, params, start_station, end_station
        FROM horizontal_elements
        WHERE alignment_id = %s
        ORDER BY start_station
    """
    return execute_query(query, (alignment_id,))

def list_vertical_elements(alignment_id: str) -> List[Dict]:
    query = """
        SELECT element_id, alignment_id, type, params, start_station, end_station
        FROM vertical_elements
        WHERE alignment_id = %s
        ORDER BY start_station
    """
    return execute_query(query, (alignment_id,))

def list_bmps(project_id: Optional[str] = None) -> List[Dict]:
    where = ""
    params: List[Any] = []
    if project_id:
        where = "WHERE b.project_id = %s"
        params.append(project_id)

    query = f"""
        SELECT
            b.bmp_id,
            b.project_id,
            proj.project_name,
            b.type,
            b.area_acres,
            b.drainage_area_acres,
            b.install_date,
            b.status,
            b.compliance,
            ST_AsGeoJSON(b.geom) AS geom,
            b.metadata
        FROM bmps b
        LEFT JOIN projects proj ON b.project_id = proj.project_id
        {where}
        ORDER BY b.install_date DESC NULLS LAST, b.bmp_id
    """
    return execute_query(query, tuple(params) if params else None)

def list_inspections(bmp_id: str) -> List[Dict]:
    query = """
        SELECT inspection_id, bmp_id, date, findings, status, follow_up
        FROM inspections
        WHERE bmp_id = %s
        ORDER BY date DESC NULLS LAST, inspection_id
    """
    return execute_query(query, (bmp_id,))

def list_maintenance_records(bmp_id: str) -> List[Dict]:
    query = """
        SELECT record_id, bmp_id, date, action, notes
        FROM maintenance_records
        WHERE bmp_id = %s
        ORDER BY date DESC NULLS LAST, record_id
    """
    return execute_query(query, (bmp_id,))

def list_utilities(project_id: Optional[str] = None) -> List[Dict]:
    where = ""
    params: List[Any] = []
    if project_id:
        where = "WHERE u.project_id = %s"
        params.append(project_id)

    query = f"""
        SELECT
            u.utility_id,
            u.project_id,
            proj.project_name,
            u.company,
            u.type,
            u.status,
            u.request_date,
            u.response_date,
            u.contact,
            u.metadata
        FROM utilities u
        LEFT JOIN projects proj ON u.project_id = proj.project_id
        {where}
        ORDER BY u.request_date DESC NULLS LAST, u.company
    """
    return execute_query(query, tuple(params) if params else None)

def list_conflicts(project_id: Optional[str] = None, utility_id: Optional[str] = None) -> List[Dict]:
    filters = []
    params: List[Any] = []
    if project_id:
        filters.append("c.project_id = %s")
        params.append(project_id)
    if utility_id:
        filters.append("c.utility_id = %s")
        params.append(utility_id)

    where = f"WHERE {' AND '.join(filters)}" if filters else ""

    query = f"""
        SELECT
            c.conflict_id,
            c.project_id,
            proj.project_name,
            c.utility_id,
            u.company AS utility_company,
            c.description,
            c.severity,
            c.resolved,
            c.suggestions,
            ST_AsGeoJSON(c.location) AS location
        FROM conflicts c
        LEFT JOIN projects proj ON c.project_id = proj.project_id
        LEFT JOIN utilities u ON c.utility_id = u.utility_id
        {where}
        ORDER BY c.severity DESC, c.conflict_id
    """
    return execute_query(query, tuple(params) if params else None)

def list_sheet_notes(project_id: Optional[str] = None) -> List[Dict]:
    where = ""
    params: List[Any] = []
    if project_id:
        where = "WHERE project_id = %s"
        params.append(project_id)

    query = f"""
        SELECT
            sn.note_id,
            sn.project_id,
            proj.project_name,
            sn.title,
            sn.category,
            sn.text,
            sn.tags,
            sn.is_standard,
            sn.created_at,
            sn.updated_at
        FROM sheet_notes sn
        LEFT JOIN projects proj ON sn.project_id = proj.project_id
        {where}
        ORDER BY sn.updated_at DESC NULLS LAST, sn.title
    """
    return execute_query(query, tuple(params) if params else None)


def get_pipe_network(network_id: str) -> Optional[Dict]:
    return execute_single(
        "SELECT network_id, project_id, name, description, created_at FROM pipe_networks WHERE network_id = %s",
        (network_id,)
    )


def create_pipe_network(project_id: Optional[str], name: Optional[str], description: Optional[str]) -> str:
    result = execute_single(
        """
        INSERT INTO pipe_networks (project_id, name, description)
        VALUES (%s, %s, %s)
        RETURNING network_id
        """,
        (project_id, name, description)
    )
    return result['network_id']


def update_pipe_network(network_id: str, updates: Dict[str, Any]) -> bool:
    assignments: List[str] = []
    params: List[Any] = []
    for field in ('project_id', 'name', 'description'):
        if field in updates and updates[field] is not None:
            assignments.append(f"{field} = %s")
            params.append(updates[field])
    return _execute_update('pipe_networks', 'network_id', network_id, assignments, params)


def delete_pipe_network(network_id: str) -> None:
    execute_query("DELETE FROM pipe_networks WHERE network_id = %s", (network_id,), fetch=False)


def get_structure(structure_id: str) -> Optional[Dict]:
    return execute_single(
        """
        SELECT structure_id, project_id, network_id, type, rim_elev, sump_depth,
               ST_AsGeoJSON(geom) AS geom, metadata
        FROM structures
        WHERE structure_id = %s
        """,
        (structure_id,)
    )


def create_structure(
    project_id: Optional[str],
    network_id: Optional[str],
    structure_type: Optional[str],
    rim_elev: Optional[float],
    sump_depth: Optional[float],
    geom: Any = None,
    srid: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    if project_id is None:
        project_id = _derive_project_id_from_network(network_id)

    geom_clause, geom_params = _build_geom_clause(geom, srid)
    params: List[Any] = [project_id, network_id, structure_type, rim_elev, sump_depth]
    params.extend(geom_params)
    params.append(_json_or_none(metadata))

    query = f"""
        INSERT INTO structures (project_id, network_id, type, rim_elev, sump_depth, geom, metadata)
        VALUES (%s, %s, %s, %s, %s, {geom_clause}, %s)
        RETURNING structure_id
    """
    result = execute_single(query, tuple(params))
    return result['structure_id']


def update_structure(structure_id: str, updates: Dict[str, Any]) -> bool:
    assignments: List[str] = []
    params: List[Any] = []

    for field in ('project_id', 'network_id', 'type', 'rim_elev', 'sump_depth'):
        if field in updates and updates[field] is not None:
            assignments.append(f"{field} = %s")
            params.append(updates[field])

    if 'metadata' in updates and updates['metadata'] is not None:
        assignments.append("metadata = %s")
        params.append(_json_or_none(updates['metadata']))

    if 'geom' in updates:
        geom_clause, geom_params = _build_geom_clause(updates['geom'], updates.get('srid'))
        assignments.append(f"geom = {geom_clause}")
        params.extend(geom_params)

    return _execute_update('structures', 'structure_id', structure_id, assignments, params)


def delete_structure(structure_id: str) -> None:
    execute_query("DELETE FROM structures WHERE structure_id = %s", (structure_id,), fetch=False)


def get_pipe(pipe_id: str) -> Optional[Dict]:
    return execute_single(
        """
        SELECT pipe_id, network_id, up_structure_id, down_structure_id, diameter_mm, material,
               slope, length_m, invert_up, invert_dn, status,
               ST_AsGeoJSON(geom) AS geom, metadata
        FROM pipes
        WHERE pipe_id = %s
        """,
        (pipe_id,)
    )


def create_pipe(
    network_id: Optional[str],
    up_structure_id: Optional[str],
    down_structure_id: Optional[str],
    diameter_mm: Optional[float],
    material: Optional[str],
    slope: Optional[float],
    length_m: Optional[float],
    invert_up: Optional[float],
    invert_dn: Optional[float],
    status: Optional[str],
    geom: Any = None,
    srid: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    geom_clause, geom_params = _build_geom_clause(geom, srid)
    params: List[Any] = [network_id, up_structure_id, down_structure_id, diameter_mm, material,
                         slope, length_m, invert_up, invert_dn, status]
    params.extend(geom_params)
    params.append(_json_or_none(metadata))

    query = f"""
        INSERT INTO pipes (
            network_id, up_structure_id, down_structure_id, diameter_mm, material,
            slope, length_m, invert_up, invert_dn, status, geom, metadata
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, {geom_clause}, %s)
        RETURNING pipe_id
    """
    result = execute_single(query, tuple(params))
    return result['pipe_id']


def update_pipe(pipe_id: str, updates: Dict[str, Any]) -> bool:
    assignments: List[str] = []
    params: List[Any] = []
    for field in (
        'network_id', 'up_structure_id', 'down_structure_id', 'diameter_mm', 'material',
        'slope', 'length_m', 'invert_up', 'invert_dn', 'status'
    ):
        if field in updates and updates[field] is not None:
            assignments.append(f"{field} = %s")
            params.append(updates[field])

    if 'metadata' in updates and updates['metadata'] is not None:
        assignments.append("metadata = %s")
        params.append(_json_or_none(updates['metadata']))

    if 'geom' in updates:
        geom_clause, geom_params = _build_geom_clause(updates['geom'], updates.get('srid'))
        assignments.append(f"geom = {geom_clause}")
        params.extend(geom_params)

    return _execute_update('pipes', 'pipe_id', pipe_id, assignments, params)


def delete_pipe(pipe_id: str) -> None:
    execute_query("DELETE FROM pipes WHERE pipe_id = %s", (pipe_id,), fetch=False)


def get_alignment(alignment_id: str) -> Optional[Dict]:
    return execute_single(
        """
        SELECT alignment_id, project_id, name, design_speed, classification, srid, station_start,
               ST_AsGeoJSON(geom) AS geom
        FROM alignments
        WHERE alignment_id = %s
        """,
        (alignment_id,)
    )


def create_alignment(
    project_id: Optional[str],
    name: Optional[str],
    design_speed: Optional[float],
    classification: Optional[str],
    srid: Optional[int],
    station_start: Optional[float],
    geom: Any = None
) -> str:
    geom_clause, geom_params = _build_geom_clause(geom, srid, default_srid=srid or 3857)
    params: List[Any] = [project_id, name, design_speed, classification, srid, station_start]
    params.extend(geom_params)

    query = f"""
        INSERT INTO alignments (project_id, name, design_speed, classification, srid, station_start, geom)
        VALUES (%s, %s, %s, %s, %s, %s, {geom_clause})
        RETURNING alignment_id
    """
    result = execute_single(query, tuple(params))
    return result['alignment_id']


def update_alignment(alignment_id: str, updates: Dict[str, Any]) -> bool:
    assignments: List[str] = []
    params: List[Any] = []
    for field in ('project_id', 'name', 'design_speed', 'classification', 'srid', 'station_start'):
        if field in updates and updates[field] is not None:
            assignments.append(f"{field} = %s")
            params.append(updates[field])

    if 'geom' in updates:
        geom_clause, geom_params = _build_geom_clause(updates['geom'], updates.get('srid'))
        assignments.append(f"geom = {geom_clause}")
        params.extend(geom_params)

    return _execute_update('alignments', 'alignment_id', alignment_id, assignments, params)


def delete_alignment(alignment_id: str) -> None:
    execute_query("DELETE FROM alignments WHERE alignment_id = %s", (alignment_id,), fetch=False)


def create_horizontal_element(alignment_id: str, payload: Dict[str, Any]) -> str:
    result = execute_single(
        """
        INSERT INTO horizontal_elements (alignment_id, type, params, start_station, end_station)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING element_id
        """,
        (
            alignment_id,
            payload.get('type'),
            _json_or_none(payload.get('params')),
            payload.get('start_station'),
            payload.get('end_station')
        )
    )
    return result['element_id']


def create_vertical_element(alignment_id: str, payload: Dict[str, Any]) -> str:
    result = execute_single(
        """
        INSERT INTO vertical_elements (alignment_id, type, params, start_station, end_station)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING element_id
        """,
        (
            alignment_id,
            payload.get('type'),
            _json_or_none(payload.get('params')),
            payload.get('start_station'),
            payload.get('end_station')
        )
    )
    return result['element_id']


def get_bmp(bmp_id: str) -> Optional[Dict]:
    return execute_single(
        """
        SELECT bmp_id, project_id, type, area_acres, drainage_area_acres, install_date,
               status, compliance, ST_AsGeoJSON(geom) AS geom, metadata
        FROM bmps
        WHERE bmp_id = %s
        """,
        (bmp_id,)
    )


def create_bmp(
    project_id: Optional[str],
    bmp_type: Optional[str],
    area_acres: Optional[float],
    drainage_area_acres: Optional[float],
    install_date: Optional[str],
    status: Optional[str],
    compliance: Optional[str],
    geom: Any = None,
    srid: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    geom_clause, geom_params = _build_geom_clause(geom, srid)
    params: List[Any] = [project_id, bmp_type, area_acres, drainage_area_acres, install_date, status, compliance]
    params.extend(geom_params)
    params.append(_json_or_none(metadata))

    query = f"""
        INSERT INTO bmps (project_id, type, area_acres, drainage_area_acres, install_date, status, compliance, geom, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, {geom_clause}, %s)
        RETURNING bmp_id
    """
    result = execute_single(query, tuple(params))
    return result['bmp_id']


def update_bmp(bmp_id: str, updates: Dict[str, Any]) -> bool:
    assignments: List[str] = []
    params: List[Any] = []
    for field in ('project_id', 'type', 'area_acres', 'drainage_area_acres', 'install_date', 'status', 'compliance'):
        if field in updates and updates[field] is not None:
            assignments.append(f"{field} = %s")
            params.append(updates[field])

    if 'metadata' in updates and updates['metadata'] is not None:
        assignments.append("metadata = %s")
        params.append(_json_or_none(updates['metadata']))

    if 'geom' in updates:
        geom_clause, geom_params = _build_geom_clause(updates['geom'], updates.get('srid'))
        assignments.append(f"geom = {geom_clause}")
        params.extend(geom_params)

    return _execute_update('bmps', 'bmp_id', bmp_id, assignments, params)


def delete_bmp(bmp_id: str) -> None:
    execute_query("DELETE FROM bmps WHERE bmp_id = %s", (bmp_id,), fetch=False)


def create_inspection_record(bmp_id: str, payload: Dict[str, Any]) -> str:
    result = execute_single(
        """
        INSERT INTO inspections (bmp_id, date, findings, status, follow_up)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING inspection_id
        """,
        (
            bmp_id,
            payload.get('date'),
            payload.get('findings'),
            payload.get('status'),
            payload.get('follow_up')
        )
    )
    return result['inspection_id']


def create_maintenance_record(bmp_id: str, payload: Dict[str, Any]) -> str:
    result = execute_single(
        """
        INSERT INTO maintenance_records (bmp_id, date, action, notes)
        VALUES (%s, %s, %s, %s)
        RETURNING record_id
        """,
        (
            bmp_id,
            payload.get('date'),
            payload.get('action'),
            payload.get('notes')
        )
    )
    return result['record_id']


def get_utility(utility_id: str) -> Optional[Dict]:
    return execute_single(
        """
        SELECT utility_id, project_id, company, type, status, request_date, response_date, contact, metadata
        FROM utilities
        WHERE utility_id = %s
        """,
        (utility_id,)
    )


def create_utility(
    project_id: Optional[str],
    company: Optional[str],
    utility_type: Optional[str],
    status: Optional[str],
    request_date: Optional[str],
    response_date: Optional[str],
    contact: Optional[str],
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    result = execute_single(
        """
        INSERT INTO utilities (project_id, company, type, status, request_date, response_date, contact, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING utility_id
        """,
        (project_id, company, utility_type, status, request_date, response_date, contact, _json_or_none(metadata))
    )
    return result['utility_id']


def update_utility(utility_id: str, updates: Dict[str, Any]) -> bool:
    assignments: List[str] = []
    params: List[Any] = []
    for field in ('project_id', 'company', 'type', 'status', 'request_date', 'response_date', 'contact'):
        if field in updates and updates[field] is not None:
            assignments.append(f"{field} = %s")
            params.append(updates[field])

    if 'metadata' in updates and updates['metadata'] is not None:
        assignments.append("metadata = %s")
        params.append(_json_or_none(updates['metadata']))

    return _execute_update('utilities', 'utility_id', utility_id, assignments, params)


def delete_utility(utility_id: str) -> None:
    execute_query("DELETE FROM utilities WHERE utility_id = %s", (utility_id,), fetch=False)


def create_conflict_record(payload: Dict[str, Any]) -> str:
    geom_clause, geom_params = _build_geom_clause(payload.get('location'), payload.get('srid'))
    params: List[Any] = [
        payload.get('project_id'),
        payload.get('utility_id'),
        payload.get('description'),
        payload.get('severity'),
        payload.get('resolved') if payload.get('resolved') is not None else False,
        payload.get('suggestions')
    ]
    params.extend(geom_params)

    query = f"""
        INSERT INTO conflicts (project_id, utility_id, description, severity, resolved, suggestions, location)
        VALUES (%s, %s, %s, %s, %s, %s, {geom_clause})
        RETURNING conflict_id
    """
    result = execute_single(query, tuple(params))
    return result['conflict_id']


def update_conflict(conflict_id: str, updates: Dict[str, Any]) -> bool:
    assignments: List[str] = []
    params: List[Any] = []
    for field in ('project_id', 'utility_id', 'description', 'severity', 'resolved', 'suggestions'):
        if field in updates and updates[field] is not None:
            assignments.append(f"{field} = %s")
            params.append(updates[field])

    if 'geom' in updates or 'location' in updates:
        geom_value = updates.get('geom', updates.get('location'))
        geom_clause, geom_params = _build_geom_clause(geom_value, updates.get('srid'))
        assignments.append(f"location = {geom_clause}")
        params.extend(geom_params)

    return _execute_update('conflicts', 'conflict_id', conflict_id, assignments, params)

if __name__ == "__main__":
    # Test connection
    print("Testing database connection...")
    try:
        with get_db_connection() as conn:
            print("✅ Database connection successful!")
            
            # Test query
            result = execute_single("SELECT COUNT(*) as count FROM block_definitions")
            print(f"✅ Found {result['count']} block definitions")
            
            result = execute_single("SELECT COUNT(*) as count FROM layer_standards")
            print(f"✅ Found {result['count']} layer standards")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
