"""
ACAD=GIS Enhanced FastAPI Server
Adds CRUD operations, file upload, and export functionality
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
import os
import tempfile
from datetime import datetime
import json
import sys
from pathlib import Path

# Ensure project root is importable when running from backend/
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# GIS extensions (optional)
try:
    from gis_api_extensions import router as gis_router, GIS_ENABLED  # type: ignore
except Exception as exc:  # pragma: no cover - optional dependency
    GIS_ENABLED = False  # type: ignore
    gis_router = None  # type: ignore
    print("⚠️ GIS extensions not available:", exc)

# Support running via `python backend/api_server.py` and as package import.
if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))
    import database  # type: ignore
    from import_dxf_georef import GeoreferencedDXFImporter  # type: ignore
else:
    from . import database  # type: ignore
    from .import_dxf_georef import GeoreferencedDXFImporter  # type: ignore

app = FastAPI(
    title="ACAD=GIS Enhanced API",
    description="REST API with full CRUD operations",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if 'gis_router' in globals() and gis_router is not None:
    app.include_router(gis_router)


@app.on_event("startup")
async def report_gis_status() -> None:
    """Log GIS availability when the server boots (works with uvicorn CLI)."""

    try:
        if GIS_ENABLED:
            print("✅ GIS Processing: ENABLED")
        else:
            print("⚠️ GIS Processing: DISABLED")
    except NameError:
        print("⚠️ GIS Processing: DISABLED")
# ============================================
# PYDANTIC MODELS
# ============================================

class ProjectCreate(BaseModel):
    project_name: str
    project_number: Optional[str] = None
    client_name: Optional[str] = None
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    project_number: Optional[str] = None
    client_name: Optional[str] = None
    description: Optional[str] = None

class DrawingCreate(BaseModel):
    project_id: str
    drawing_name: str
    drawing_number: Optional[str] = None
    drawing_type: Optional[str] = None
    scale: Optional[str] = None
    description: Optional[str] = None

class DrawingUpdate(BaseModel):
    drawing_name: Optional[str] = None
    drawing_number: Optional[str] = None
    drawing_type: Optional[str] = None
    scale: Optional[str] = None
    description: Optional[str] = None

# ============================================
# CIVIL TOOLS MODELS (stubs)
# ============================================

class PipeNetworkCreate(BaseModel):
    project_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None

class StructureCreate(BaseModel):
    project_id: Optional[str] = None
    network_id: Optional[str] = None
    type: Optional[str] = None
    rim_elev: Optional[float] = None
    sump_depth: Optional[float] = None
    geom: Optional[Any] = None
    srid: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class PipeCreate(BaseModel):
    network_id: Optional[str] = None
    up_structure_id: Optional[str] = None
    down_structure_id: Optional[str] = None
    diameter_mm: Optional[float] = None
    material: Optional[str] = None
    slope: Optional[float] = None
    length_m: Optional[float] = None
    invert_up: Optional[float] = None
    invert_dn: Optional[float] = None
    status: Optional[str] = None
    geom: Optional[Any] = None
    srid: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class AlignmentCreate(BaseModel):
    project_id: Optional[str] = None
    name: Optional[str] = None
    design_speed: Optional[float] = None
    classification: Optional[str] = None
    srid: Optional[int] = None
    station_start: Optional[float] = None
    geom: Optional[Any] = None

class BMPCreate(BaseModel):
    project_id: Optional[str] = None
    type: Optional[str] = None
    area_acres: Optional[float] = None
    drainage_area_acres: Optional[float] = None
    install_date: Optional[str] = None
    status: Optional[str] = None
    compliance: Optional[str] = None
    geom: Optional[Any] = None
    srid: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class UtilityCreate(BaseModel):
    project_id: Optional[str] = None
    company: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    request_date: Optional[str] = None
    response_date: Optional[str] = None
    contact: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ConflictCreate(BaseModel):
    project_id: Optional[str] = None
    utility_id: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    resolved: Optional[bool] = None
    suggestions: Optional[List[str]] = None
    location: Optional[Any] = None
    geom: Optional[Any] = None
    srid: Optional[int] = None

# ============================================
# HELPERS
# ============================================

def parse_bbox(bbox: Optional[str]) -> Optional[tuple]:
    if not bbox:
        return None
    try:
        parts = [float(part.strip()) for part in bbox.split(',')]
        if len(parts) != 4:
            raise ValueError
        return tuple(parts)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid bbox. Use minx,miny,maxx,maxy")


def build_feature_collection(rows: List[Dict[str, Any]], geom_field: str = 'geom') -> Dict[str, Any]:
    features = []
    for row in rows:
        geometry_raw = row.get(geom_field)
        geometry = None
        if geometry_raw:
            if isinstance(geometry_raw, str):
                try:
                    geometry = json.loads(geometry_raw)
                except json.JSONDecodeError:
                    geometry = None
            elif isinstance(geometry_raw, dict):
                geometry = geometry_raw

        properties = {k: v for k, v in row.items() if k != geom_field}
        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        })

    return {"type": "FeatureCollection", "features": features}


PIPE_SLOPE_MINIMUMS = [
    (4, 0.50),
    (6, 0.40),
    (8, 0.40),
    (10, 0.28),
    (12, 0.33),
    (15, 0.25),
    (18, 0.19),
    (24, 0.15)
]

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "ACAD=GIS Enhanced API Server",
        "version": "2.0.0"
    }

@app.get("/api/health")
def health_check():
    try:
        with database.get_db_connection() as conn:
            result = database.execute_single("SELECT COUNT(*) as count FROM projects")
            return {
                "status": "healthy",
                "database": "connected",
                "projects_count": result['count']
            }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

# ============================================
# STATISTICS
# ============================================

@app.get("/api/stats")
def get_statistics():
    try:
        stats = {}
        
        result = database.execute_single("SELECT COUNT(*) as count FROM projects")
        stats['total_projects'] = result['count']
        
        result = database.execute_single("SELECT COUNT(*) as count FROM drawings")
        stats['total_drawings'] = result['count']
        
        result = database.execute_single("SELECT COUNT(*) as count FROM block_definitions")
        stats['total_symbols'] = result['count']
        
        result = database.execute_single("SELECT COUNT(*) as count FROM layer_standards")
        stats['total_layers'] = result['count']
        
        recent_drawings = database.execute_query(
            "SELECT drawing_name, created_at FROM drawings ORDER BY created_at DESC LIMIT 5"
        )
        stats['recent_drawings'] = recent_drawings
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# ============================================
# PROJECTS - FULL CRUD
# ============================================

@app.get("/api/projects")
def get_projects():
    """Get all projects with drawing counts"""
    try:
        query = """
            SELECT 
                p.*,
                COUNT(d.drawing_id) as drawing_count
            FROM projects p
            LEFT JOIN drawings d ON p.project_id = d.project_id
            GROUP BY p.project_id
            ORDER BY p.created_at DESC
        """
        projects = database.execute_query(query)
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")

@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    """Get single project details"""
    try:
        project = database.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")

@app.post("/api/projects")
def create_project(project: ProjectCreate):
    """Create new project"""
    try:
        project_id = database.create_project(
            project_name=project.project_name,
            project_number=project.project_number,
            client_name=project.client_name,
            description=project.description
        )
        
        return {
            "project_id": project_id,
            "message": "Project created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@app.put("/api/projects/{project_id}")
def update_project(project_id: str, project: ProjectUpdate):
    """Update existing project"""
    try:
        # Check if project exists
        existing = database.get_project(project_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = []
        
        if project.project_name is not None:
            update_fields.append("project_name = %s")
            params.append(project.project_name)
        if project.project_number is not None:
            update_fields.append("project_number = %s")
            params.append(project.project_number)
        if project.client_name is not None:
            update_fields.append("client_name = %s")
            params.append(project.client_name)
        if project.description is not None:
            update_fields.append("description = %s")
            params.append(project.description)
        
        if not update_fields:
            return {"message": "No fields to update"}
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(project_id)
        
        query = f"UPDATE projects SET {', '.join(update_fields)} WHERE project_id = %s"
        database.execute_query(query, tuple(params))
        
        return {"message": "Project updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str):
    """Delete project (will cascade to drawings if configured)"""
    try:
        # Check if project exists
        existing = database.get_project(project_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if project has drawings
        drawings = database.execute_query(
            "SELECT COUNT(*) as count FROM drawings WHERE project_id = %s",
            (project_id,)
        )
        drawing_count = drawings[0]['count'] if drawings else 0
        
        if drawing_count > 0:
            # You might want to prevent deletion or cascade
            # For now, we'll prevent it and return an error
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete project with {drawing_count} drawings. Delete drawings first."
            )
        
        database.execute_query("DELETE FROM projects WHERE project_id = %s", (project_id,))
        
        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")

# ============================================
# DRAWINGS - FULL CRUD
# ============================================

@app.get("/api/projects/{project_id}/drawings")
def get_project_drawings(project_id: str):
    """Get all drawings for a project"""
    try:
        query = """
            SELECT 
                drawing_id,
                drawing_name,
                drawing_number,
                drawing_type,
                scale,
                description,
                created_at,
                updated_at,
                is_georeferenced,
                CASE 
                    WHEN dxf_content IS NOT NULL THEN true 
                    ELSE false 
                END as has_content
            FROM drawings
            WHERE project_id = %s
            ORDER BY drawing_number, drawing_name
        """
        drawings = database.execute_query(query, (project_id,))
        return drawings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get drawings: {str(e)}")

@app.get("/api/drawings")
def get_all_drawings(limit: int = 100, search: Optional[str] = None):
    """Get all drawings with optional search"""
    try:
        if search:
            query = """
                SELECT 
                    d.drawing_id,
                    d.drawing_name,
                    d.drawing_number,
                    d.drawing_type,
                    d.scale,
                    d.created_at,
                    d.is_georeferenced,
                    d.drawing_epsg_code,
                    d.drawing_coordinate_system,
                    p.project_name,
                    p.project_id,
                    p.project_number,
                    CASE 
                        WHEN d.dxf_content IS NOT NULL THEN true 
                        ELSE false 
                    END as has_content
                FROM drawings d
                LEFT JOIN projects p ON d.project_id = p.project_id
                WHERE d.drawing_name ILIKE %s OR d.drawing_number ILIKE %s OR p.project_name ILIKE %s
                ORDER BY d.created_at DESC
                LIMIT %s
            """
            search_term = f"%{search}%"
            drawings = database.execute_query(query, (search_term, search_term, search_term, limit))
        else:
            query = """
                SELECT 
                    d.drawing_id,
                    d.drawing_name,
                    d.drawing_number,
                    d.drawing_type,
                    d.scale,
                    d.created_at,
                    d.is_georeferenced,
                    d.drawing_epsg_code,
                    d.drawing_coordinate_system,
                    p.project_name,
                    p.project_id,
                    p.project_number,
                    CASE 
                        WHEN d.dxf_content IS NOT NULL THEN true 
                        ELSE false 
                    END as has_content
                FROM drawings d
                LEFT JOIN projects p ON d.project_id = p.project_id
                ORDER BY d.created_at DESC
                LIMIT %s
            """
            drawings = database.execute_query(query, (limit,))
        
        return drawings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get drawings: {str(e)}")

@app.get("/api/drawings/{drawing_id}")
def get_drawing(drawing_id: str):
    """Get basic drawing information"""
    try:
        drawing = database.get_drawing(drawing_id)
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        if 'dxf_content' in drawing:
            drawing['has_dxf_content'] = drawing['dxf_content'] is not None
            del drawing['dxf_content']
        
        return drawing
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get drawing: {str(e)}")

@app.post("/api/drawings")
def create_drawing(drawing: DrawingCreate):
    """Create new drawing"""
    try:
        drawing_id = database.create_drawing(
            project_id=drawing.project_id,
            drawing_name=drawing.drawing_name,
            drawing_number=drawing.drawing_number,
            drawing_type=drawing.drawing_type,
            scale=drawing.scale,
            description=drawing.description
        )
        
        return {
            "drawing_id": drawing_id,
            "message": "Drawing created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create drawing: {str(e)}")

@app.put("/api/drawings/{drawing_id}")
def update_drawing(drawing_id: str, drawing: DrawingUpdate):
    """Update existing drawing"""
    try:
        # Check if drawing exists
        existing = database.get_drawing(drawing_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if drawing.drawing_name is not None:
            update_fields.append("drawing_name = %s")
            params.append(drawing.drawing_name)
        if drawing.drawing_number is not None:
            update_fields.append("drawing_number = %s")
            params.append(drawing.drawing_number)
        if drawing.drawing_type is not None:
            update_fields.append("drawing_type = %s")
            params.append(drawing.drawing_type)
        if drawing.scale is not None:
            update_fields.append("scale = %s")
            params.append(drawing.scale)
        if drawing.description is not None:
            update_fields.append("description = %s")
            params.append(drawing.description)
        
        if not update_fields:
            return {"message": "No fields to update"}
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(drawing_id)
        
        query = f"UPDATE drawings SET {', '.join(update_fields)} WHERE drawing_id = %s"
        database.execute_query(query, tuple(params))
        
        return {"message": "Drawing updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update drawing: {str(e)}")

@app.delete("/api/drawings/{drawing_id}")
def delete_drawing(drawing_id: str):
    """Delete drawing"""
    try:
        # Check if drawing exists
        existing = database.get_drawing(drawing_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Delete associated data first (layers, inserts, etc.)
        database.execute_query("DELETE FROM block_inserts WHERE drawing_id = %s", (drawing_id,))
        database.execute_query("DELETE FROM layers WHERE drawing_id = %s", (drawing_id,))
        database.execute_query("DELETE FROM drawings WHERE drawing_id = %s", (drawing_id,))
        
        return {"message": "Drawing deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete drawing: {str(e)}")

# ============================================
# DRAWING VIEWER DATA
# ============================================

@app.get("/api/drawings/{drawing_id}/render")
def get_drawing_render_data(drawing_id: str, limit: int = 2500):
    """Get all data needed to render a drawing"""
    try:
        # Get basic drawing info
        drawing = database.get_drawing(drawing_id)
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # Get layers
        layers = database.get_layers(drawing_id)
        
        # Get block inserts with symbol details
        query = """
            SELECT 
                bi.insert_id,
                bi.insert_x,
                bi.insert_y,
                bi.insert_z,
                bi.scale_x,
                bi.scale_y,
                bi.rotation,
                bi.layout_name,
                bi.metadata,
                bd.block_id,
                bd.block_name,
                bd.svg_content,
                bd.category,
                bd.domain,
                bd.semantic_type,
                bd.semantic_label,
                bd.description as block_description,
                bd.svg_viewbox
            FROM block_inserts bi
            JOIN block_definitions bd ON bi.block_id = bd.block_id
            WHERE bi.drawing_id = %s
            ORDER BY bi.created_at
            LIMIT %s
        """
        inserts = database.execute_query(query, (drawing_id, limit))
        
        # Calculate drawing bounds
        bounds = calculate_drawing_bounds(inserts)
        
        # Check total count
        count_query = "SELECT COUNT(*) as total_count FROM block_inserts WHERE drawing_id = %s"
        total_result = database.execute_single(count_query, (drawing_id,))
        total_inserts = total_result['total_count'] if total_result else 0
        is_truncated = total_inserts > limit
        
        return {
            "drawing": {
                "drawing_id": drawing['drawing_id'],
                "drawing_name": drawing['drawing_name'],
                "drawing_number": drawing.get('drawing_number'),
                "is_georeferenced": drawing.get('is_georeferenced', False),
                "drawing_coordinate_system": drawing.get('drawing_coordinate_system'),
                "drawing_epsg_code": drawing.get('drawing_epsg_code')
            },
            "layers": layers,
            "inserts": inserts,
            "bounds": bounds,
            "stats": {
                "insert_count": len(inserts),
                "total_inserts": total_inserts,
                "is_truncated": is_truncated,
                "layer_count": len(layers)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get drawing data: {str(e)}")

@app.get("/api/drawings/{drawing_id}/extent")
def get_drawing_extent(drawing_id: str, srid: Optional[int] = Query(4326)):
    """Return full drawing bounds (no row limit) and EPSG code.

    Bounds are computed from canonical_features when available (transformed to the
    requested SRID, default 4326). If no canonical data exists, falls back to
    raw block inserts in native units.
    """
    try:
        drawing = database.get_drawing(drawing_id)
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")

        target_srid = int(srid) if srid else 4326

        canonical_bounds = database.execute_single(
            """
            SELECT
                ST_XMin(extent) AS min_x,
                ST_YMin(extent) AS min_y,
                ST_XMax(extent) AS max_x,
                ST_YMax(extent) AS max_y,
                feature_count
            FROM (
                SELECT
                    ST_Extent(ST_Transform(geom, %s)) AS extent,
                    COUNT(*) AS feature_count
                FROM canonical_features
                WHERE drawing_id = %s
                  AND geom IS NOT NULL
            ) AS bounds
            """,
            (target_srid, drawing_id)
        )

        if canonical_bounds and canonical_bounds.get("min_x") is not None:
            bounds = {
                "min_x": float(canonical_bounds["min_x"]),
                "min_y": float(canonical_bounds["min_y"]),
                "max_x": float(canonical_bounds["max_x"]),
                "max_y": float(canonical_bounds["max_y"]),
            }
            feature_count = canonical_bounds.get("feature_count", 0)
            source = "canonical_features"
        else:
            fallback = database.execute_single(
                """
                SELECT
                    MIN(insert_x) AS min_x,
                    MIN(insert_y) AS min_y,
                    MAX(insert_x) AS max_x,
                    MAX(insert_y) AS max_y,
                    COUNT(*)      AS feature_count
                FROM block_inserts
                WHERE drawing_id = %s
                """,
                (drawing_id,)
            )

            feature_count = fallback.get('feature_count', 0) if fallback else 0
            if not fallback or fallback['min_x'] is None or fallback['min_y'] is None:
                bounds = {"min_x": 0, "min_y": 0, "max_x": 0, "max_y": 0}
            else:
                bounds = {
                    "min_x": float(fallback['min_x']),
                    "min_y": float(fallback['min_y']),
                    "max_x": float(fallback['max_x']),
                    "max_y": float(fallback['max_y'])
                }
            source = "block_inserts"

        canonical_total_row = database.execute_single(
            """
            SELECT COUNT(*) AS canonical_count
            FROM canonical_features
            WHERE drawing_id = %s
              AND geom IS NOT NULL
            """,
            (drawing_id,)
        )
        canonical_total = canonical_total_row['canonical_count'] if canonical_total_row else 0

        return {
            "drawing_epsg_code": drawing.get('drawing_epsg_code'),
            "requested_srid": target_srid,
            "bounds": bounds,
            "stats": {
                "feature_count": feature_count,
                "canonical_count": canonical_total,
                "source": source
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get drawing extent: {str(e)}")


@app.get("/api/drawings/{drawing_id}/geojson")
def get_drawing_geojson(
    drawing_id: str,
    bbox: Optional[str] = Query(None, description="minx,miny,maxx,maxy in EPSG:4326"),
    srid: Optional[int] = Query(4326, description="Target SRID for output"),
    simplify: Optional[float] = Query(None, description="Simplification tolerance"),
    limit: Optional[int] = Query(None, ge=1, le=10000)
):
    """Return canonical features as GeoJSON."""
    try:
        drawing = database.get_drawing(drawing_id)
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")

        bbox_values = parse_bbox(bbox)
        target_srid = int(srid) if srid else 4326
        tolerance = float(simplify) if simplify else None

        rows = database.list_canonical_features(
            drawing_id=drawing_id,
            bbox=bbox_values,
            target_srid=target_srid,
            simplify_tolerance=tolerance,
            limit=limit
        )

        collection = build_feature_collection(rows)
        collection["count"] = len(rows)
        collection["srid"] = target_srid
        if bbox_values:
            collection["request_bbox"] = bbox_values
        if tolerance:
            collection["simplify"] = tolerance
        if limit:
            collection["limit"] = limit
        collection["source"] = "canonical_features"
        collection["drawing_id"] = drawing_id

        return collection
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build drawing GeoJSON: {str(e)}")

def calculate_drawing_bounds(inserts):
    """Calculate bounding box for drawing"""
    if not inserts:
        return {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0}
    
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    for insert in inserts:
        if insert.get('insert_x') is not None:
            min_x = min(min_x, insert['insert_x'])
            max_x = max(max_x, insert['insert_x'])
        if insert.get('insert_y') is not None:
            min_y = min(min_y, insert['insert_y'])
            max_y = max(max_y, insert['insert_y'])
    
    return {
        "min_x": min_x if min_x != float('inf') else 0,
        "max_x": max_x if max_x != float('-inf') else 0,
        "min_y": min_y if min_y != float('inf') else 0,
        "max_y": max_y if max_y != float('-inf') else 0
    }

# ============================================
# IMPORT/EXPORT
# ============================================

@app.post("/api/import/dxf")
async def import_dxf(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    drawing_name: Optional[str] = Form(None),
    is_georeferenced: bool = Form(False),
    epsg_code: Optional[str] = Form(None)
):
    """Import DXF file and persist canonical features."""
    tmp_path = None
    try:
        # Validate file type
        filename_lower = (file.filename or "").lower()
        if not filename_lower.endswith('.dxf'):
            raise HTTPException(status_code=400, detail="Only DXF files are supported")

        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded DXF is empty")

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        override_epsg = None
        if epsg_code:
            try:
                override_epsg = int(epsg_code)
            except ValueError:
                raise HTTPException(status_code=400, detail="EPSG code must be numeric")

        importer = GeoreferencedDXFImporter(
            tmp_path,
            project_id,
            force_georef=is_georeferenced,
            override_epsg=override_epsg
        )

        final_name = drawing_name or os.path.splitext(file.filename)[0]
        drawing_id = importer.run(final_name)

        return {
            "success": True,
            "message": f"DXF file '{file.filename}' imported successfully",
            "drawing_id": drawing_id,
            "drawing_name": final_name,
            "project_id": project_id,
            "bytes_received": len(content),
            "is_georeferenced": importer.is_georeferenced,
            "epsg_code": importer.epsg_code,
            "coordinate_system": importer.coordinate_system,
            "stats": importer.stats
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import DXF: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

@app.get("/api/export/{drawing_id}")
def export_drawing(drawing_id: str, format: str = "dxf"):
    """Export drawing to DXF or other format"""
    try:
        drawing = database.get_drawing(drawing_id)
        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")
        
        # TODO: Implement actual export logic
        # For now, return a placeholder
        return {
            "success": False,
            "message": "Export functionality needs to be implemented",
            "drawing_id": drawing_id,
            "format": format
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export drawing: {str(e)}")

@app.post("/api/export/{format}")
def export_generic(format: str, payload: Dict[str, Any] = None):
    return {
        "success": True,
        "message": f"Export stub: {format}",
        "request": payload or {}
    }

# ============================================
# CIVIL TOOLS ENDPOINTS
# ============================================

# Pipe Networks
@app.get("/api/pipe-networks")
def list_pipe_networks(project_id: Optional[str] = None):
    return database.list_pipe_networks(project_id)

@app.post("/api/pipe-networks")
def create_pipe_network(payload: PipeNetworkCreate):
    network_id = database.create_pipe_network(
        payload.project_id,
        payload.name,
        payload.description
    )
    return {"network_id": network_id}

@app.get("/api/pipe-networks/{network_id}")
def get_pipe_network(network_id: str):
    network = database.get_pipe_network(network_id)
    if not network:
        raise HTTPException(status_code=404, detail="Pipe network not found")
    return network

@app.get("/api/pipe-networks/{network_id}/detail")
def get_pipe_network_detail(network_id: str):
    detail = database.get_pipe_network_detail(network_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Pipe network not found")
    return detail

@app.put("/api/pipe-networks/{network_id}")
def update_pipe_network(network_id: str, payload: PipeNetworkCreate):
    updated = database.update_pipe_network(network_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=400, detail="No changes provided")
    return {"network_id": network_id, "updated": True}

@app.delete("/api/pipe-networks/{network_id}")
def delete_pipe_network(network_id: str):
    database.delete_pipe_network(network_id)
    return {"network_id": network_id, "deleted": True}

# Pipes
@app.get("/api/pipes")
def list_pipes(network_id: Optional[str] = None):
    return database.list_pipes(network_id)

@app.post("/api/pipes")
def create_pipe(payload: PipeCreate):
    pipe_id = database.create_pipe(
        payload.network_id,
        payload.up_structure_id,
        payload.down_structure_id,
        payload.diameter_mm,
        payload.material,
        payload.slope,
        payload.length_m,
        payload.invert_up,
        payload.invert_dn,
        payload.status,
        payload.geom,
        payload.srid,
        payload.metadata
    )
    return {"pipe_id": pipe_id}

@app.get("/api/pipes/{pipe_id}")
def get_pipe(pipe_id: str):
    pipe = database.get_pipe(pipe_id)
    if not pipe:
        raise HTTPException(status_code=404, detail="Pipe not found")
    return pipe

@app.put("/api/pipes/{pipe_id}")
def update_pipe(pipe_id: str, payload: PipeCreate):
    updated = database.update_pipe(pipe_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=400, detail="No changes provided")
    return {"pipe_id": pipe_id, "updated": True}

@app.delete("/api/pipes/{pipe_id}")
def delete_pipe(pipe_id: str):
    database.delete_pipe(pipe_id)
    return {"pipe_id": pipe_id, "deleted": True}

# Structures
@app.get("/api/structures")
def list_structures(network_id: Optional[str] = None, project_id: Optional[str] = None):
    return database.list_structures(network_id=network_id, project_id=project_id)

@app.post("/api/structures")
def create_structure(payload: StructureCreate):
    structure_id = database.create_structure(
        payload.project_id,
        payload.network_id,
        payload.type,
        payload.rim_elev,
        payload.sump_depth,
        payload.geom,
        payload.srid,
        payload.metadata
    )
    return {"structure_id": structure_id}

@app.get("/api/structures/{structure_id}")
def get_structure(structure_id: str):
    structure = database.get_structure(structure_id)
    if not structure:
        raise HTTPException(status_code=404, detail="Structure not found")
    return structure

@app.put("/api/structures/{structure_id}")
def update_structure(structure_id: str, payload: StructureCreate):
    updated = database.update_structure(structure_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=400, detail="No changes provided")
    return {"structure_id": structure_id, "updated": True}

@app.delete("/api/structures/{structure_id}")
def delete_structure(structure_id: str):
    database.delete_structure(structure_id)
    return {"structure_id": structure_id, "deleted": True}

# Alignments
@app.get("/api/alignments")
def list_alignments(project_id: Optional[str] = None):
    return database.list_alignments(project_id)

@app.post("/api/alignments")
def create_alignment(payload: AlignmentCreate):
    alignment_id = database.create_alignment(
        payload.project_id,
        payload.name,
        payload.design_speed,
        payload.classification,
        payload.srid,
        payload.station_start,
        payload.geom
    )
    return {"alignment_id": alignment_id}

@app.get("/api/alignments/{alignment_id}")
def get_alignment(alignment_id: str):
    alignment = database.get_alignment(alignment_id)
    if not alignment:
        raise HTTPException(status_code=404, detail="Alignment not found")
    alignment['horizontal_elements'] = database.list_horizontal_elements(alignment_id)
    alignment['vertical_elements'] = database.list_vertical_elements(alignment_id)
    return alignment

@app.put("/api/alignments/{alignment_id}")
def update_alignment(alignment_id: str, payload: AlignmentCreate):
    updated = database.update_alignment(alignment_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=400, detail="No changes provided")
    return {"alignment_id": alignment_id, "updated": True}

@app.delete("/api/alignments/{alignment_id}")
def delete_alignment(alignment_id: str):
    database.delete_alignment(alignment_id)
    return {"alignment_id": alignment_id, "deleted": True}

@app.get("/api/alignments/{alignment_id}/horizontal-elements")
def list_horizontal_elements(alignment_id: str):
    return database.list_horizontal_elements(alignment_id)

@app.post("/api/alignments/{alignment_id}/horizontal-elements")
def create_horizontal_element(alignment_id: str, payload: Dict[str, Any]):
    element_id = database.create_horizontal_element(alignment_id, payload)
    return {"element_id": element_id}

@app.get("/api/alignments/{alignment_id}/vertical-elements")
def list_vertical_elements(alignment_id: str):
    return database.list_vertical_elements(alignment_id)

@app.post("/api/alignments/{alignment_id}/vertical-elements")
def create_vertical_element(alignment_id: str, payload: Dict[str, Any]):
    element_id = database.create_vertical_element(alignment_id, payload)
    return {"element_id": element_id}

# BMPs
@app.get("/api/bmps")
def list_bmps(project_id: Optional[str] = None):
    return database.list_bmps(project_id)

@app.post("/api/bmps")
def create_bmp(payload: BMPCreate):
    bmp_id = database.create_bmp(
        payload.project_id,
        payload.type,
        payload.area_acres,
        payload.drainage_area_acres,
        payload.install_date,
        payload.status,
        payload.compliance,
        payload.geom,
        payload.srid,
        payload.metadata
    )
    return {"bmp_id": bmp_id}

@app.get("/api/bmps/{bmp_id}")
def get_bmp(bmp_id: str):
    bmp = database.get_bmp(bmp_id)
    if not bmp:
        raise HTTPException(status_code=404, detail="BMP not found")
    bmp['inspections'] = database.list_inspections(bmp_id)
    bmp['maintenance'] = database.list_maintenance_records(bmp_id)
    return bmp

@app.put("/api/bmps/{bmp_id}")
def update_bmp(bmp_id: str, payload: BMPCreate):
    updated = database.update_bmp(bmp_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=400, detail="No changes provided")
    return {"bmp_id": bmp_id, "updated": True}

@app.delete("/api/bmps/{bmp_id}")
def delete_bmp(bmp_id: str):
    database.delete_bmp(bmp_id)
    return {"bmp_id": bmp_id, "deleted": True}

@app.get("/api/bmps/{bmp_id}/inspections")
def list_bmp_inspections(bmp_id: str):
    return database.list_inspections(bmp_id)

@app.post("/api/bmps/{bmp_id}/inspections")
def create_bmp_inspection(bmp_id: str, payload: Dict[str, Any]):
    inspection_id = database.create_inspection_record(bmp_id, payload)
    return {"inspection_id": inspection_id}

@app.get("/api/bmps/{bmp_id}/maintenance")
def list_bmp_maintenance(bmp_id: str):
    return database.list_maintenance_records(bmp_id)

@app.post("/api/bmps/{bmp_id}/maintenance")
def create_bmp_maintenance(bmp_id: str, payload: Dict[str, Any]):
    record_id = database.create_maintenance_record(bmp_id, payload)
    return {"record_id": record_id}

# Utilities & Conflicts
@app.get("/api/utilities")
def list_utilities(project_id: Optional[str] = None):
    return database.list_utilities(project_id)

@app.post("/api/utilities")
def create_utility(payload: UtilityCreate):
    utility_id = database.create_utility(
        payload.project_id,
        payload.company,
        payload.type,
        payload.status,
        payload.request_date,
        payload.response_date,
        payload.contact,
        payload.metadata
    )
    return {"utility_id": utility_id}

@app.get("/api/utilities/{utility_id}")
def get_utility(utility_id: str):
    utility = database.get_utility(utility_id)
    if not utility:
        raise HTTPException(status_code=404, detail="Utility not found")
    return utility

@app.put("/api/utilities/{utility_id}")
def update_utility(utility_id: str, payload: UtilityCreate):
    updated = database.update_utility(utility_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=400, detail="No changes provided")
    return {"utility_id": utility_id, "updated": True}

@app.delete("/api/utilities/{utility_id}")
def delete_utility(utility_id: str):
    database.delete_utility(utility_id)
    return {"utility_id": utility_id, "deleted": True}

@app.get("/api/conflicts")
def list_conflicts(project_id: Optional[str] = None, utility_id: Optional[str] = None):
    return database.list_conflicts(project_id=project_id, utility_id=utility_id)

@app.post("/api/conflicts")
def create_conflict(payload: ConflictCreate):
    conflict_id = database.create_conflict_record(payload.dict(exclude_unset=True))
    return {"conflict_id": conflict_id}

@app.put("/api/conflicts/{conflict_id}")
def update_conflict(conflict_id: str, payload: Dict[str, Any]):
    updated = database.update_conflict(conflict_id, payload)
    if not updated:
        raise HTTPException(status_code=400, detail="No changes provided")
    return {"conflict_id": conflict_id, "updated": True}

@app.get("/api/sheet-notes")
def list_sheet_notes(project_id: Optional[str] = None):
    return database.list_sheet_notes(project_id)

# GeoJSON endpoints (empty feature collections)
@app.get("/api/pipes/geojson")
def pipes_geojson(
    bbox: Optional[str] = None,
    srid: Optional[int] = None,
    limit: Optional[int] = None,
    network_id: Optional[str] = None
):
    filters = []
    params: List[Any] = []

    if network_id:
        filters.append("p.network_id = %s")
        params.append(network_id)

    bbox_values = parse_bbox(bbox)
    if bbox_values:
        minx, miny, maxx, maxy = bbox_values
        filters.append("p.geom && ST_MakeEnvelope(%s, %s, %s, %s, %s)")
        params.extend([minx, miny, maxx, maxy, srid or 3857])

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    query = f"""
        SELECT
            p.pipe_id,
            p.network_id,
            p.diameter_mm,
            p.material,
            p.slope,
            p.length_m,
            p.status,
            ST_AsGeoJSON(p.geom) AS geom
        FROM pipes p
        {where_clause}
        ORDER BY p.pipe_id
    """
    if limit:
        query += " LIMIT %s"
        params.append(limit)

    rows = database.execute_query(query, tuple(params) if params else None)
    return build_feature_collection(rows)

@app.get("/api/structures/geojson")
def structures_geojson(
    bbox: Optional[str] = None,
    srid: Optional[int] = None,
    limit: Optional[int] = None,
    network_id: Optional[str] = None
):
    filters = []
    params: List[Any] = []

    if network_id:
        filters.append("s.network_id = %s")
        params.append(network_id)

    bbox_values = parse_bbox(bbox)
    if bbox_values:
        minx, miny, maxx, maxy = bbox_values
        filters.append("s.geom && ST_MakeEnvelope(%s, %s, %s, %s, %s)")
        params.extend([minx, miny, maxx, maxy, srid or 3857])

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    query = f"""
        SELECT
            s.structure_id,
            s.network_id,
            s.type,
            s.rim_elev,
            s.sump_depth,
            ST_AsGeoJSON(s.geom) AS geom
        FROM structures s
        {where_clause}
        ORDER BY s.structure_id
    """
    if limit:
        query += " LIMIT %s"
        params.append(limit)

    rows = database.execute_query(query, tuple(params) if params else None)
    return build_feature_collection(rows)

@app.get("/api/alignments/{alignment_id}/geojson")
def alignment_geojson(alignment_id: str):
    alignment = database.get_alignment(alignment_id)
    if not alignment:
        raise HTTPException(status_code=404, detail="Alignment not found")
    return build_feature_collection([alignment])

@app.get("/api/bmps/geojson")
def bmps_geojson(
    bbox: Optional[str] = None,
    srid: Optional[int] = None,
    type: Optional[str] = None,
    project_id: Optional[str] = None,
    limit: Optional[int] = None
):
    filters = []
    params: List[Any] = []

    if project_id:
        filters.append("b.project_id = %s")
        params.append(project_id)

    if type:
        filters.append("b.type = %s")
        params.append(type)

    bbox_values = parse_bbox(bbox)
    if bbox_values:
        minx, miny, maxx, maxy = bbox_values
        filters.append("b.geom && ST_MakeEnvelope(%s, %s, %s, %s, %s)")
        params.extend([minx, miny, maxx, maxy, srid or 3857])

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    query = f"""
        SELECT
            b.bmp_id,
            b.project_id,
            b.type,
            b.status,
            b.compliance,
            ST_AsGeoJSON(b.geom) AS geom
        FROM bmps b
        {where_clause}
        ORDER BY b.bmp_id
    """
    if limit:
        query += " LIMIT %s"
        params.append(limit)

    rows = database.execute_query(query, tuple(params) if params else None)
    return build_feature_collection(rows)

# Validation
@app.post("/api/validate/pipe-slope")
def validate_pipe_slope(scope: Dict[str, Any]):
    network_id = scope.get('network_id')
    project_id = scope.get('project_id')

    pipes = database.fetch_pipe_slopes(project_id=project_id, network_id=network_id)

    results: List[Dict[str, Any]] = []
    violations: List[Dict[str, Any]] = []
    for pipe in pipes:
        required = pipe.get('required_slope')
        actual = pipe.get('slope')
        ok = True
        if required is not None and actual is not None:
            ok = actual >= required
        elif required is not None:
            ok = False

        entry = {
            "pipe_id": pipe.get('pipe_id'),
            "network_id": pipe.get('network_id'),
            "network_name": pipe.get('network_name'),
            "project_id": pipe.get('project_id'),
            "project_name": pipe.get('project_name'),
            "diameter_mm": pipe.get('diameter_mm'),
            "required_slope": required,
            "actual_slope": actual,
            "slope_margin": pipe.get('slope_margin'),
            "length_m": pipe.get('length_m'),
            "status": pipe.get('status'),
            "ok": ok
        }
        results.append(entry)
        if not ok:
            violations.append(entry)

    message = f"Checked {len(results)} pipes"
    if violations:
        message += f" • {len(violations)} below minimum"

    summary = {
        "count": len(results),
        "violations": len(violations),
        "networks": sorted({(pipe['network_id'], pipe['network_name']) for pipe in pipes}, key=lambda item: item[1])
    }

    return {"success": True, "message": message, "results": results, "violations": violations, "summary": summary}

def validate_velocity(scope: Dict[str, Any]):
    return {"success": False, "message": "Velocity validation not implemented yet", "results": []}

@app.post("/api/clash-detection")
def clash_detection(scope: Dict[str, Any]):
    return {"success": False, "message": "Clash detection not implemented yet", "conflicts": []}

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    print("Starting ACAD-GIS Enhanced API Server...")
    print("Server running at: http://localhost:8000")
    print("API Docs at: http://localhost:8000/docs")
    print("Press CTRL+C to stop")
    try:
        if GIS_ENABLED:
            print("✅ GIS Processing: ENABLED")
        else:
            print("⚠️ GIS Processing: DISABLED")
    except NameError:
        print("⚠️ GIS Processing: DISABLED")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8000)
