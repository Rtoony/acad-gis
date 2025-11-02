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
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

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


def _required_slope_sql(alias: str = "p") -> str:
    """Return SQL CASE expression for minimum slope based on diameter (inches)."""
    return f"""
    CASE
        WHEN {alias}.diameter_mm IS NULL THEN NULL
        WHEN ({alias}.diameter_mm / 25.4) >= 24 THEN 0.15
        WHEN ({alias}.diameter_mm / 25.4) >= 18 THEN 0.19
        WHEN ({alias}.diameter_mm / 25.4) >= 15 THEN 0.25
        WHEN ({alias}.diameter_mm / 25.4) >= 12 THEN 0.33
        WHEN ({alias}.diameter_mm / 25.4) >= 10 THEN 0.28
        WHEN ({alias}.diameter_mm / 25.4) >= 8 THEN 0.40
        WHEN ({alias}.diameter_mm / 25.4) >= 6 THEN 0.40
        WHEN ({alias}.diameter_mm / 25.4) >= 4 THEN 0.50
        ELSE 0.60
    END
    """


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
    
    # Check if layer already exists
    existing = execute_single(
        "SELECT layer_id FROM layers WHERE drawing_id = %s AND layer_name = %s",
        (drawing_id, layer_name)
    )

    if existing:
        # Update existing layer
        execute_query(
            """
            UPDATE layers SET
                color = %s,
                linetype = %s,
                lineweight = %s,
                layer_standard_id = %s
            WHERE layer_id = %s
            """,
            (color, linetype, lineweight, layer_standard_id, existing['layer_id']),
            fetch=False
        )
        return existing['layer_id']

    query = """
        INSERT INTO layers (
            layer_id, drawing_id, layer_name, color, linetype, lineweight,
            is_plottable, is_locked, is_frozen, layer_standard_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
# CANONICAL FEATURES
# ============================================

def clear_canonical_features(drawing_id: str):
    """Remove canonical features for a drawing prior to re-import."""
    query = "DELETE FROM canonical_features WHERE drawing_id = %s"
    execute_query(query, (drawing_id,), fetch=False)


def insert_canonical_feature(
    drawing_id: str,
    project_id: str,
    feature_type: str,
    layer_name: Optional[str],
    native_wkt: Optional[str],
    native_srid: Optional[int],
    canonical_wkt: Optional[str],
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """Persist a canonical feature record and return its feature_id."""
    query = """
        INSERT INTO canonical_features (
            feature_id,
            drawing_id,
            project_id,
            feature_type,
            layer_name,
            native_geom,
            native_srid,
            geom,
            metadata
        )
        VALUES (
            gen_random_uuid(),
            %s,
            %s,
            %s,
            %s,
            CASE
                WHEN %s IS NULL THEN NULL
                ELSE ST_SetSRID(ST_GeomFromText(%s), COALESCE(%s, 0))
            END,
            %s,
            CASE
                WHEN %s IS NULL THEN NULL
                ELSE ST_SetSRID(ST_GeomFromText(%s), 4326)
            END,
            %s
        )
        RETURNING feature_id
    """
    metadata_json = Json(metadata) if metadata is not None else None

    result = execute_single(
        query,
        (
            drawing_id,
            project_id,
            feature_type,
            layer_name,
            native_wkt,
            native_wkt,
            native_srid,
            native_srid,
            canonical_wkt,
            canonical_wkt,
            metadata_json,
        ),
    )
    return result['feature_id'] if result else None


def list_canonical_features(
    drawing_id: str,
    bbox: Optional[tuple] = None,
    target_srid: Optional[int] = 4326,
    simplify_tolerance: Optional[float] = None,
    limit: Optional[int] = None
) -> List[Dict]:
    """
    Return canonical features for a drawing, optionally filtered by bbox and simplified.
    Adds layer metadata (color, ids) so the map can style features consistently.
    """
    srid = target_srid or 4326
    geom_expr = "cf.geom"
    params: List[Any] = []

    if srid != 4326:
        geom_expr = "ST_Transform(cf.geom, %s)"
        params.append(srid)

    if simplify_tolerance and simplify_tolerance > 0:
        geom_expr = f"ST_SimplifyPreserveTopology({geom_expr}, %s)"
        params.append(simplify_tolerance)

    query = f"""
        SELECT
            cf.feature_id,
            cf.drawing_id,
            cf.project_id,
            cf.feature_type,
            cf.layer_name,
            ST_AsGeoJSON({geom_expr}) AS geom,
            cf.metadata,
            l.layer_id,
            COALESCE(l.layer_standard_id, ls.layer_standard_id) AS layer_standard_id,
            COALESCE(l.color, ls.color) AS layer_color_index,
            ls.color_rgb AS layer_color_rgb,
            COALESCE(ls.color_name, l.metadata ->> 'color_name') AS layer_color_name
        FROM canonical_features cf
        LEFT JOIN layers l
          ON l.drawing_id = cf.drawing_id
         AND l.layer_name = cf.layer_name
        LEFT JOIN layer_standards ls
          ON (
               (l.layer_standard_id IS NOT NULL AND ls.layer_standard_id = l.layer_standard_id)
               OR (l.layer_standard_id IS NULL AND ls.layer_name = cf.layer_name)
             )
        WHERE cf.drawing_id = %s
          AND cf.geom IS NOT NULL
    """
    params.append(drawing_id)

    if bbox:
        query += """
          AND cf.geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)
        """
        params.extend(bbox)

    query += """
        ORDER BY cf.layer_name, cf.feature_type, cf.feature_id
    """

    if limit:
        query += " LIMIT %s"
        params.append(limit)

    return execute_query(query, tuple(params))

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
    """Return pipe networks with aggregated slope statistics."""
    where = ""
    params: List[Any] = []
    if project_id:
        where = "WHERE pn.project_id = %s"
        params.append(project_id)

    req = _required_slope_sql("p")
    metrics_subquery = f"""
        SELECT
            p.network_id,
            COUNT(*) AS pipe_count,
            SUM(CASE WHEN p.slope IS NOT NULL AND ({req}) IS NOT NULL AND p.slope < ({req}) THEN 1 ELSE 0 END) AS pipes_below_min,
            AVG(p.slope) AS avg_slope,
            MIN(p.slope - ({req})) AS worst_margin
        FROM pipes p
        GROUP BY p.network_id
    """

    query = f"""
        SELECT
            pn.network_id,
            pn.project_id,
            proj.project_name,
            pn.name,
            pn.description,
            pn.created_at,
            metrics.pipe_count,
            metrics.pipes_below_min,
            metrics.avg_slope,
            metrics.worst_margin
        FROM pipe_networks pn
        LEFT JOIN projects proj ON pn.project_id = proj.project_id
        LEFT JOIN ({metrics_subquery}) metrics ON metrics.network_id = pn.network_id
        {where}
        ORDER BY pn.created_at DESC NULLS LAST, pn.name
    """
    rows = execute_query(query, tuple(params) if params else None)
    for row in rows:
        if row.get('pipe_count') is not None:
            row['pipe_count'] = int(row['pipe_count'])
        if row.get('pipes_below_min') is not None:
            row['pipes_below_min'] = int(row['pipes_below_min'])
        row['avg_slope'] = _to_float(row.get('avg_slope'))
        row['worst_margin'] = _to_float(row.get('worst_margin'))
    return rows

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
            s.invert_elev,
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
    """Return pipes with optional network filter and slope metrics."""
    where = ""
    params: List[Any] = []
    if network_id:
        where = "WHERE p.network_id = %s"
        params.append(network_id)

    req = _required_slope_sql("p")
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
            ({req}) AS required_slope,
            p.slope - ({req}) AS slope_margin,
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
    rows = execute_query(query, tuple(params) if params else None)
    for row in rows:
        row['slope'] = _to_float(row.get('slope'))
        row['required_slope'] = _to_float(row.get('required_slope'))
        row['slope_margin'] = _to_float(row.get('slope_margin'))
        row['length_m'] = _to_float(row.get('length_m'))
        row['invert_up'] = _to_float(row.get('invert_up'))
        row['invert_dn'] = _to_float(row.get('invert_dn'))
        if row.get('diameter_mm') is not None:
            row['diameter_mm'] = float(row['diameter_mm'])
    return rows


def fetch_pipe_slopes(project_id: Optional[str] = None, network_id: Optional[str] = None) -> List[Dict]:
    """Fetch pipe slope details filtered by project or network."""
    filters = []
    params: List[Any] = []
    if project_id:
        filters.append("pn.project_id = %s")
        params.append(project_id)
    if network_id:
        filters.append("p.network_id = %s")
        params.append(network_id)

    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    req = _required_slope_sql("p")
    query = f"""
        SELECT
            p.pipe_id,
            p.network_id,
            pn.name AS network_name,
            pn.project_id,
            proj.project_name,
            p.up_structure_id,
            p.down_structure_id,
            p.diameter_mm,
            p.material,
            p.slope,
            ({req}) AS required_slope,
            p.slope - ({req}) AS slope_margin,
            p.length_m,
            p.invert_up,
            p.invert_dn,
            p.status,
            ST_AsGeoJSON(p.geom) AS geom,
            p.metadata
        FROM pipes p
        LEFT JOIN pipe_networks pn ON p.network_id = pn.network_id
        LEFT JOIN projects proj ON pn.project_id = proj.project_id
        {where}
        ORDER BY proj.project_name, pn.name, p.pipe_id
    """
    rows = execute_query(query, tuple(params) if params else None)
    for row in rows:
        row['slope'] = _to_float(row.get('slope'))
        row['required_slope'] = _to_float(row.get('required_slope'))
        row['slope_margin'] = _to_float(row.get('slope_margin'))
        row['length_m'] = _to_float(row.get('length_m'))
        row['invert_up'] = _to_float(row.get('invert_up'))
        row['invert_dn'] = _to_float(row.get('invert_dn'))
        if row.get('diameter_mm') is not None:
            row['diameter_mm'] = float(row['diameter_mm'])
    return rows

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

def list_alignment_pis(alignment_id: str) -> List[Dict]:
    """Return alignment vertices as PI-like points with approximate stationing.
    Uses ST_DumpPoints and ST_LineLocatePoint to compute station along the line.
    """
    query = """
        WITH a AS (
            SELECT station_start, geom
            FROM alignments
            WHERE alignment_id = %s
        )
        SELECT
            (dp.path)[1] AS vertex_index,
            (a.station_start + ST_Length(a.geom) * ST_LineLocatePoint(a.geom, dp.geom)) AS station,
            ST_X(dp.geom) AS easting,
            ST_Y(dp.geom) AS northing,
            ST_Z(dp.geom) AS elevation,
            ST_AsGeoJSON(dp.geom) AS geometry
        FROM a, LATERAL ST_DumpPoints(a.geom) AS dp
        ORDER BY vertex_index
    """
    rows = execute_query(query, (alignment_id,))
    # Normalize numeric types
    for r in rows:
        r['station'] = _to_float(r.get('station'))
        r['easting'] = _to_float(r.get('easting'))
        r['northing'] = _to_float(r.get('northing'))
        r['elevation'] = _to_float(r.get('elevation'))
    return rows

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
        where = "WHERE sn.project_id = %s"
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
        SELECT structure_id, project_id, network_id, type, rim_elev, sump_depth, invert_elev,
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
    invert_elev: Optional[float] = None,
    geom: Any = None,
    srid: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    if project_id is None:
        project_id = _derive_project_id_from_network(network_id)

    geom_clause, geom_params = _build_geom_clause(geom, srid)
    params: List[Any] = [project_id, network_id, structure_type, rim_elev, sump_depth, invert_elev]
    params.extend(geom_params)
    params.append(_json_or_none(metadata))

    query = f"""
        INSERT INTO structures (project_id, network_id, type, rim_elev, sump_depth, invert_elev, geom, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, {geom_clause}, %s)
        RETURNING structure_id
    """
    result = execute_single(query, tuple(params))
    return result['structure_id']


def update_structure(structure_id: str, updates: Dict[str, Any]) -> bool:
    assignments: List[str] = []
    params: List[Any] = []

    for field in ('project_id', 'network_id', 'type', 'rim_elev', 'sump_depth', 'invert_elev'):
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

# ============================================
# SHEET NOTE MANAGER HELPERS
# ============================================

def list_sheet_note_sets(project_id: str) -> List[Dict]:
    """Return note sets for a project with note_count."""
    return execute_query(
        """
        SELECT s.set_id, s.project_id, s.set_name, s.description, s.discipline,
               s.is_active, s.created_at, s.updated_at,
               COUNT(n.project_note_id) AS note_count
        FROM sheet_note_sets s
        LEFT JOIN project_sheet_notes n ON n.set_id = s.set_id
        WHERE s.project_id = %s
        GROUP BY s.set_id
        ORDER BY s.created_at DESC
        """,
        (project_id,)
    )

def create_sheet_note_set(payload: Dict[str, Any]) -> Dict:
    row = execute_single(
        """
        INSERT INTO sheet_note_sets (project_id, set_name, description, discipline, is_active)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            payload.get('project_id'), payload.get('set_name'), payload.get('description'),
            payload.get('discipline'), bool(payload.get('is_active', False))
        )
    )
    return row or {}

def update_sheet_note_set(set_id: str, updates: Dict[str, Any]) -> Dict:
    fields = []
    params: List[Any] = []
    for key in ('set_name', 'description', 'discipline', 'is_active'):
        if key in updates:
            fields.append(f"{key} = %s")
            params.append(updates[key])
    if not fields:
        return execute_single("SELECT * FROM sheet_note_sets WHERE set_id = %s", (set_id,)) or {}
    fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(set_id)
    execute_query(f"UPDATE sheet_note_sets SET {', '.join(fields)} WHERE set_id = %s", tuple(params), fetch=False)
    return execute_single("SELECT * FROM sheet_note_sets WHERE set_id = %s", (set_id,)) or {}

def delete_sheet_note_set(set_id: str) -> None:
    execute_query("DELETE FROM sheet_note_sets WHERE set_id = %s", (set_id,), fetch=False)

def activate_sheet_note_set(project_id: str, set_id: str) -> None:
    execute_query("UPDATE sheet_note_sets SET is_active = FALSE WHERE project_id = %s", (project_id,), fetch=False)
    execute_query("UPDATE sheet_note_sets SET is_active = TRUE WHERE set_id = %s", (set_id,), fetch=False)

def list_project_sheet_notes(set_id: str) -> List[Dict]:
    return execute_query(
        """
        SELECT p.project_note_id, p.set_id, p.standard_note_id, p.display_code,
               p.custom_title, p.custom_text, p.is_modified, p.sort_order, p.usage_count,
               p.created_at, p.updated_at,
               s.note_title AS standard_title, s.note_text AS standard_text,
               s.note_category, s.discipline
        FROM project_sheet_notes p
        LEFT JOIN standard_notes s ON p.standard_note_id = s.note_id
        WHERE p.set_id = %s
        ORDER BY p.sort_order, p.created_at
        """,
        (set_id,)
    )

def _next_sort_order(set_id: str) -> int:
    row = execute_single("SELECT COALESCE(MAX(sort_order), 0) AS max FROM project_sheet_notes WHERE set_id = %s", (set_id,))
    return int((row or {}).get('max', 0)) + 1

def create_project_sheet_note(payload: Dict[str, Any]) -> Dict:
    set_id = payload.get('set_id')
    std_id = payload.get('standard_note_id')
    display_code = payload.get('display_code')
    custom_title = payload.get('custom_title')
    custom_text = payload.get('custom_text')
    is_modified = bool(custom_title or custom_text)
    sort_order = _next_sort_order(set_id)
    row = execute_single(
        """
        INSERT INTO project_sheet_notes (set_id, standard_note_id, display_code, custom_title, custom_text, is_modified, sort_order)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (set_id, std_id, display_code, custom_title, custom_text, is_modified, sort_order)
    )
    return row or {}

def update_project_sheet_note(project_note_id: str, updates: Dict[str, Any]) -> Dict:
    fields = []
    params: List[Any] = []
    for key in ('display_code', 'custom_title', 'custom_text'):
        if key in updates:
            fields.append(f"{key} = %s")
            params.append(updates[key])
    if 'custom_title' in updates or 'custom_text' in updates:
        fields.append("is_modified = %s")
        params.append(True)
    if not fields:
        return execute_single("SELECT * FROM project_sheet_notes WHERE project_note_id = %s", (project_note_id,)) or {}
    fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(project_note_id)
    execute_query(f"UPDATE project_sheet_notes SET {', '.join(fields)} WHERE project_note_id = %s", tuple(params), fetch=False)
    return execute_single("SELECT * FROM project_sheet_notes WHERE project_note_id = %s", (project_note_id,)) or {}

def delete_project_sheet_note(project_note_id: str) -> None:
    execute_query("DELETE FROM project_sheet_notes WHERE project_note_id = %s", (project_note_id,), fetch=False)

def reorder_project_sheet_note(project_note_id: str, new_order: int) -> None:
    execute_query("UPDATE project_sheet_notes SET sort_order = %s WHERE project_note_id = %s", (new_order, project_note_id), fetch=False)

def list_sheet_note_assignments(
    drawing_id: Optional[str] = None,
    layout_name: Optional[str] = None,
    project_note_id: Optional[str] = None
) -> List[Dict]:
    if project_note_id:
        return execute_query(
            """
            SELECT a.assignment_id, a.project_note_id, a.drawing_id, a.layout_name,
                   a.legend_sequence, a.show_in_legend, a.assigned_at, a.assigned_by,
                   d.drawing_name, d.drawing_number,
                   p.project_name
            FROM sheet_note_assignments a
            LEFT JOIN drawings d ON a.drawing_id = d.drawing_id
            LEFT JOIN projects p ON d.project_id = p.project_id
            WHERE a.project_note_id = %s
            ORDER BY a.assigned_at DESC
            """,
            (project_note_id,)
        )
    if drawing_id:
        return execute_query(
            """
            SELECT a.assignment_id, a.project_note_id, a.drawing_id, a.layout_name,
                   a.legend_sequence, a.show_in_legend, a.assigned_at, a.assigned_by,
                   n.display_code,
                   n.standard_note_id,
                   n.is_modified,
                   COALESCE(n.custom_title, s.note_title) AS note_title,
                   COALESCE(n.custom_text, s.note_text) AS note_text
            FROM sheet_note_assignments a
            LEFT JOIN project_sheet_notes n ON a.project_note_id = n.project_note_id
            LEFT JOIN standard_notes s ON n.standard_note_id = s.note_id
            WHERE a.drawing_id = %s AND (%s IS NULL OR a.layout_name = %s)
            ORDER BY a.legend_sequence
            """,
            (drawing_id, layout_name, layout_name)
        )
    return []

def create_sheet_note_assignment(payload: Dict[str, Any]) -> Dict:
    row = execute_single(
        """
        INSERT INTO sheet_note_assignments (project_note_id, drawing_id, layout_name, legend_sequence, show_in_legend, assigned_by)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            payload['project_note_id'], payload['drawing_id'], payload.get('layout_name') or 'Model',
            payload['legend_sequence'], bool(payload.get('show_in_legend', True)), payload.get('assigned_by')
        )
    )
    # increment usage_count
    execute_query("UPDATE project_sheet_notes SET usage_count = usage_count + 1 WHERE project_note_id = %s", (payload['project_note_id'],), fetch=False)
    return row or {}

def delete_sheet_note_assignment(assignment_id: str) -> None:
    # need project_note_id to decrement usage
    row = execute_single("SELECT project_note_id FROM sheet_note_assignments WHERE assignment_id = %s", (assignment_id,))
    execute_query("DELETE FROM sheet_note_assignments WHERE assignment_id = %s", (assignment_id,), fetch=False)
    if row and row.get('project_note_id'):
        execute_query("UPDATE project_sheet_notes SET usage_count = GREATEST(usage_count - 1, 0) WHERE project_note_id = %s", (row['project_note_id'],), fetch=False)

def build_sheet_note_legend(drawing_id: str, layout_name: Optional[str]) -> Dict:
    items = list_sheet_note_assignments(drawing_id=drawing_id, layout_name=layout_name)
    legend = []
    for it in items:
        legend.append({
            'legend_sequence': it['legend_sequence'],
            'display_code': it.get('display_code') or '',
            'note_title': it.get('note_title') or '',
            'note_text': it.get('note_text') or '',
            'standard_note_id': it.get('standard_note_id'),
            'is_modified': bool(it.get('is_modified'))
        })
    return { 'drawing_id': drawing_id, 'layout_name': layout_name or 'Model', 'legend': legend, 'total_notes': len(legend) }

# ============================================
# SHEET SET MANAGER HELPERS
# ============================================

def list_sheet_sets(project_id: str) -> List[Dict]:
    return execute_query(
        """
        SELECT s.*, COUNT(sh.sheet_id) AS sheet_count,
               p.project_name, p.project_number
        FROM sheet_sets s
        LEFT JOIN sheets sh ON sh.set_id = s.set_id
        LEFT JOIN projects p ON p.project_id = s.project_id
        WHERE s.project_id = %s
        GROUP BY s.set_id, p.project_name, p.project_number
        ORDER BY s.created_at DESC
        """,
        (project_id,)
    )

def create_sheet_set(payload: Dict[str, Any]) -> Dict:
    row = execute_single(
        """
        INSERT INTO sheet_sets (project_id, set_name, description, phase, discipline, status, issued_date, issued_to)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            payload.get('project_id'), payload.get('set_name'), payload.get('description'),
            payload.get('phase'), payload.get('discipline'), payload.get('status', 'Draft'),
            payload.get('issued_date'), payload.get('issued_to')
        )
    )
    return row or {}

def update_sheet_set(set_id: str, updates: Dict[str, Any]) -> Dict:
    fields = []
    params: List[Any] = []
    for key in ('set_name', 'description', 'phase', 'discipline', 'status', 'issued_date', 'issued_to'):
        if key in updates:
            fields.append(f"{key} = %s")
            params.append(updates[key])
    if not fields:
        return execute_single("SELECT * FROM sheet_sets WHERE set_id = %s", (set_id,)) or {}
    fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(set_id)
    execute_query(f"UPDATE sheet_sets SET {', '.join(fields)} WHERE set_id = %s", tuple(params), fetch=False)
    return execute_single("SELECT * FROM sheet_sets WHERE set_id = %s", (set_id,)) or {}

def delete_sheet_set(set_id: str) -> None:
    execute_query("DELETE FROM sheet_sets WHERE set_id = %s", (set_id,), fetch=False)

def list_sheets(set_id: str) -> List[Dict]:
    return execute_query(
        """
        SELECT sh.*, CASE WHEN a.assignment_id IS NULL THEN 'unassigned' ELSE 'assigned' END AS assignment_status,
               a.drawing_id, a.layout_name
        FROM sheets sh
        LEFT JOIN LATERAL (
            SELECT assignment_id, drawing_id, layout_name
            FROM sheet_drawing_assignments a
            WHERE a.sheet_id = sh.sheet_id
            ORDER BY a.assigned_at DESC
            LIMIT 1
        ) a ON TRUE
        WHERE sh.set_id = %s
        ORDER BY COALESCE(sh.sheet_hierarchy_number, 50), sh.sheet_code
        """,
        (set_id,)
    )

def renumber_sheets(set_id: str) -> int:
    sheets = execute_query(
        """
        SELECT sheet_id FROM sheets
        WHERE set_id = %s
        ORDER BY COALESCE(sheet_hierarchy_number,50), sheet_code
        """,
        (set_id,)
    )
    count = 0
    for idx, sh in enumerate(sheets, start=1):
        execute_query("UPDATE sheets SET sheet_number = %s WHERE sheet_id = %s", (idx, sh['sheet_id']), fetch=False)
        count += 1
    return count

def create_sheet(payload: Dict[str, Any]) -> Dict:
    row = execute_single(
        """
        INSERT INTO sheets (set_id, sheet_code, sheet_title, discipline_code, sheet_type, sheet_category, sheet_hierarchy_number, scale, sheet_size, template_id, revision_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            payload['set_id'], payload.get('sheet_code'), payload.get('sheet_title'), payload.get('discipline_code'),
            payload.get('sheet_type'), payload.get('sheet_category'), payload.get('sheet_hierarchy_number', 50),
            payload.get('scale'), payload.get('sheet_size','24x36'), payload.get('template_id'), payload.get('revision_number', 0)
        )
    )
    # auto-renumber
    renumber_sheets(payload['set_id'])
    return row or {}

def update_sheet(sheet_id: str, updates: Dict[str, Any]) -> Dict:
    fields = []
    params: List[Any] = []
    for key in ('sheet_code','sheet_title','discipline_code','sheet_type','sheet_category','sheet_hierarchy_number','scale','sheet_size','template_id','revision_number','revision_date','notes'):
        if key in updates:
            fields.append(f"{key} = %s")
            params.append(updates[key])
    if not fields:
        return execute_single("SELECT * FROM sheets WHERE sheet_id = %s", (sheet_id,)) or {}
    fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(sheet_id)
    execute_query(f"UPDATE sheets SET {', '.join(fields)} WHERE sheet_id = %s", tuple(params), fetch=False)
    return execute_single("SELECT * FROM sheets WHERE sheet_id = %s", (sheet_id,)) or {}

def delete_sheet(sheet_id: str) -> None:
    execute_query("DELETE FROM sheets WHERE sheet_id = %s", (sheet_id,), fetch=False)


# ============================================
# SHEET SET MANAGER – ADDITIONAL HELPERS
# ============================================

def list_sheet_drawing_assignments(sheet_id: str) -> List[Dict]:
    return execute_query(
        """
        SELECT a.assignment_id, a.sheet_id, a.drawing_id, a.layout_name,
               a.assigned_at, a.assigned_by, a.notes,
               d.drawing_name
        FROM sheet_drawing_assignments a
        LEFT JOIN drawings d ON a.drawing_id = d.drawing_id
        WHERE a.sheet_id = %s
        ORDER BY a.assigned_at DESC
        """,
        (sheet_id,)
    )


def create_sheet_drawing_assignment(payload: Dict[str, Any]) -> Dict:
    row = execute_single(
        """
        INSERT INTO sheet_drawing_assignments (sheet_id, drawing_id, layout_name, assigned_by, notes)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            payload['sheet_id'], payload.get('drawing_id'), payload.get('layout_name'),
            payload.get('assigned_by'), payload.get('notes')
        )
    )
    return row or {}


def delete_sheet_drawing_assignment(assignment_id: str) -> None:
    execute_query("DELETE FROM sheet_drawing_assignments WHERE assignment_id = %s", (assignment_id,), fetch=False)


def list_sheet_revisions(sheet_id: str) -> List[Dict]:
    return execute_query(
        """
        SELECT revision_id, sheet_id, revision_number, revision_date, description,
               revised_by, reference_number, created_at
        FROM sheet_revisions
        WHERE sheet_id = %s
        ORDER BY revision_date DESC, created_at DESC
        """,
        (sheet_id,)
    )


def create_sheet_revision(payload: Dict[str, Any]) -> Dict:
    row = execute_single(
        """
        INSERT INTO sheet_revisions (sheet_id, revision_number, revision_date, description, revised_by, reference_number)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            payload['sheet_id'], payload['revision_number'], payload['revision_date'],
            payload.get('description'), payload.get('revised_by'), payload.get('reference_number')
        )
    )
    return row or {}


def list_sheet_relationships(sheet_id: str) -> List[Dict]:
    return execute_query(
        """
        SELECT r.relationship_id, r.source_sheet_id, r.target_sheet_id, r.relationship_type, r.notes, r.created_at,
               s1.sheet_code AS source_sheet_code, s1.sheet_title AS source_sheet_title,
               s2.sheet_code AS target_sheet_code, s2.sheet_title AS target_sheet_title
        FROM sheet_relationships r
        LEFT JOIN sheets s1 ON r.source_sheet_id = s1.sheet_id
        LEFT JOIN sheets s2 ON r.target_sheet_id = s2.sheet_id
        WHERE r.source_sheet_id = %s OR r.target_sheet_id = %s
        ORDER BY r.created_at DESC
        """,
        (sheet_id, sheet_id)
    )


def create_sheet_relationship(payload: Dict[str, Any]) -> Dict:
    row = execute_single(
        """
        INSERT INTO sheet_relationships (source_sheet_id, target_sheet_id, relationship_type, notes)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """,
        (
            payload['source_sheet_id'], payload['target_sheet_id'], payload['relationship_type'], payload.get('notes')
        )
    )
    return row or {}


def delete_sheet_relationship(relationship_id: str) -> None:
    execute_query("DELETE FROM sheet_relationships WHERE relationship_id = %s", (relationship_id,), fetch=False)


def generate_sheet_index(set_id: str) -> Dict:
    rows = execute_query(
        """
        SELECT sheet_number, sheet_code, sheet_title, scale, revision_number, revision_date
        FROM sheets
        WHERE set_id = %s
        ORDER BY sheet_number NULLS LAST, COALESCE(sheet_hierarchy_number,50), sheet_code
        """,
        (set_id,)
    )
    return { 'set_id': set_id, 'sheets': rows, 'total_sheets': len(rows) }


# ============================================
# PROJECT DETAILS HELPERS
# ============================================

def get_project_details(project_id: str) -> Optional[Dict]:
    return execute_single(
        """
        SELECT project_id, street_address, city, state, zip_code, county, apn,
               project_engineer, project_manager, design_lead,
               client_contact_name, client_contact_email, client_contact_phone,
               jurisdiction, jurisdiction_type, permit_number, project_type, project_phase,
               tb_format_type, tb_format_size, design_start_date, design_completion_date,
               construction_start_date, special_requirements, notes, created_at, updated_at
        FROM project_details
        WHERE project_id = %s
        """,
        (project_id,)
    )


def create_project_details(payload: Dict[str, Any]) -> Dict:
    row = execute_single(
        """
        INSERT INTO project_details (
            project_id, street_address, city, state, zip_code, county, apn,
            project_engineer, project_manager, design_lead,
            client_contact_name, client_contact_email, client_contact_phone,
            jurisdiction, jurisdiction_type, permit_number, project_type, project_phase,
            tb_format_type, tb_format_size, design_start_date, design_completion_date,
            construction_start_date, special_requirements, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            payload['project_id'], payload.get('street_address'), payload.get('city'), payload.get('state'),
            payload.get('zip_code'), payload.get('county'), payload.get('apn'),
            payload.get('project_engineer'), payload.get('project_manager'), payload.get('design_lead'),
            payload.get('client_contact_name'), payload.get('client_contact_email'), payload.get('client_contact_phone'),
            payload.get('jurisdiction'), payload.get('jurisdiction_type'), payload.get('permit_number'),
            payload.get('project_type'), payload.get('project_phase'),
            payload.get('tb_format_type'), payload.get('tb_format_size'),
            payload.get('design_start_date'), payload.get('design_completion_date'),
            payload.get('construction_start_date'), payload.get('special_requirements'), payload.get('notes')
        )
    )
    return row or {}


def update_project_details(project_id: str, updates: Dict[str, Any]) -> Dict:
    fields = []
    params: List[Any] = []
    for key in (
        'street_address', 'city', 'state', 'zip_code', 'county', 'apn',
        'project_engineer', 'project_manager', 'design_lead',
        'client_contact_name', 'client_contact_email', 'client_contact_phone',
        'jurisdiction', 'jurisdiction_type', 'permit_number', 'project_type', 'project_phase',
        'tb_format_type', 'tb_format_size', 'design_start_date', 'design_completion_date',
        'construction_start_date', 'special_requirements', 'notes'
    ):
        if key in updates:
            fields.append(f"{key} = %s")
            params.append(updates[key])
    if not fields:
        return get_project_details(project_id) or {}
    fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(project_id)
    execute_query(f"UPDATE project_details SET {', '.join(fields)} WHERE project_id = %s", tuple(params), fetch=False)
    return get_project_details(project_id) or {}


# ============================================
# STANDARD NOTES (LIBRARY) HELPERS
# ============================================

def list_standard_notes(
    note_category: Optional[str] = None,
    discipline: Optional[str] = None,
    q: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[Dict]:
    filters: List[str] = []
    params: List[Any] = []
    if note_category:
        filters.append("note_category = %s")
        params.append(note_category)
    if discipline:
        filters.append("discipline = %s")
        params.append(discipline)
    if is_active is not None:
        filters.append("is_active = %s")
        params.append(is_active)
    if q:
        filters.append("(note_title ILIKE %s OR note_text ILIKE %s)")
        like = f"%{q}%"
        params.extend([like, like])
    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    query = f"""
        SELECT note_id, note_category, note_title, note_text, discipline, created_at, updated_at, is_active
        FROM standard_notes
        {where}
        ORDER BY note_category NULLS LAST, note_title
    """
    return execute_query(query, tuple(params) if params else None)

def get_pipe_network_detail(network_id: str) -> Optional[Dict]:
    network = execute_single(
        """
        SELECT
            pn.network_id,
            pn.project_id,
            pn.name,
            pn.description,
            pn.created_at,
            proj.project_name,
            proj.project_number,
            proj.client_name
        FROM pipe_networks pn
        LEFT JOIN projects proj ON pn.project_id = proj.project_id
        WHERE pn.network_id = %s
        """,
        (network_id,)
    )
    if not network:
        return None

    pipes = fetch_pipe_slopes(network_id=network_id)
    pipe_count = len(pipes)
    pipes_below_min = sum(
        1 for p in pipes
        if p['required_slope'] is not None and p['slope'] is not None and p['slope'] < p['required_slope']
    )
    slope_values = [p['slope'] for p in pipes if p['slope'] is not None]
    avg_slope = sum(slope_values) / len(slope_values) if slope_values else None
    slope_margins = [p['slope_margin'] for p in pipes if p['slope_margin'] is not None]
    worst_margin = min(slope_margins) if slope_margins else None

    structures = list_structures(network_id=network_id)
    for struct in structures:
        struct['rim_elev'] = _to_float(struct.get('rim_elev'))
        struct['sump_depth'] = _to_float(struct.get('sump_depth'))
        geom = struct.pop('geom', None)
        if geom:
            try:
                coords = json.loads(geom)['coordinates']
                struct['longitude'], struct['latitude'] = coords[0], coords[1]
            except Exception:
                struct['longitude'] = struct['latitude'] = None

    conflicts = execute_query(
        """
        SELECT
            c.conflict_id,
            c.description,
            c.severity,
            c.resolved,
            c.suggestions,
            ST_AsGeoJSON(c.location) AS location,
            u.company,
            u.type,
            u.status
        FROM conflicts c
        LEFT JOIN utilities u ON c.utility_id = u.utility_id
        WHERE c.project_id = %s
        ORDER BY c.severity DESC, c.conflict_id
        """,
        (network['project_id'],)
    )
    for item in conflicts:
        geom = item.pop('location', None)
        if geom:
            try:
                coords = json.loads(geom)['coordinates']
                item['longitude'], item['latitude'] = coords[0], coords[1]
            except Exception:
                item['longitude'] = item['latitude'] = None

    notes = execute_query(
        """
        SELECT note_id, title, category, text, tags, is_standard, updated_at
        FROM sheet_notes
        WHERE project_id = %s
        ORDER BY is_standard DESC, updated_at DESC
        LIMIT 10
        """,
        (network['project_id'],)
    )

    summary = {
        'pipe_count': pipe_count,
        'pipes_below_min': pipes_below_min,
        'avg_slope': _to_float(avg_slope),
        'worst_margin': _to_float(worst_margin),
        'slope_samples': len(slope_values)
    }

    return {
        'network': network,
        'summary': summary,
        'pipes': pipes,
        'structures': structures,
        'conflicts': conflicts,
        'notes': notes
    }


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

def update_horizontal_element(element_id: str, updates: Dict[str, Any]) -> bool:
    assignments: List[str] = []
    params: List[Any] = []
    for field in ('type', 'start_station', 'end_station'):
        if field in updates and updates[field] is not None:
            assignments.append(f"{field} = %s")
            params.append(updates[field])
    if 'params' in updates and updates['params'] is not None:
        assignments.append("params = %s")
        params.append(_json_or_none(updates['params']))
    return _execute_update('horizontal_elements', 'element_id', element_id, assignments, params)

def delete_horizontal_element(element_id: str) -> None:
    execute_query("DELETE FROM horizontal_elements WHERE element_id = %s", (element_id,), fetch=False)

def update_vertical_element(element_id: str, updates: Dict[str, Any]) -> bool:
    assignments: List[str] = []
    params: List[Any] = []
    for field in ('type', 'start_station', 'end_station'):
        if field in updates and updates[field] is not None:
            assignments.append(f"{field} = %s")
            params.append(updates[field])
    if 'params' in updates and updates['params'] is not None:
        assignments.append("params = %s")
        params.append(_json_or_none(updates['params']))
    return _execute_update('vertical_elements', 'element_id', element_id, assignments, params)

def delete_vertical_element(element_id: str) -> None:
    execute_query("DELETE FROM vertical_elements WHERE element_id = %s", (element_id,), fetch=False)


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
