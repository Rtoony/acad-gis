"""
Survey & Civil Engineering API routes
Provides CRUD endpoints for survey points and basic lookups.
"""

from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
import json
import csv
import io

from . import database
from psycopg2.extras import Json  # type: ignore

router = APIRouter()


class GeometryInput(BaseModel):
    geojson: Dict[str, Any] = Field(..., description="GeoJSON geometry (Point)")
    srid: Optional[int] = Field(2226, description="SRID of provided geometry")


class SurveyPointCreate(BaseModel):
    project_id: str
    point_number: str
    point_type: Optional[str] = None
    point_description: Optional[str] = None
    point_code: Optional[str] = None
    geometry: Optional[GeometryInput] = None
    northing: Optional[float] = None
    easting: Optional[float] = None
    elevation: Optional[float] = None
    survey_date: Optional[str] = None
    surveyed_by: Optional[str] = None
    survey_method: Optional[str] = None
    instrument_used: Optional[str] = None
    horizontal_accuracy: Optional[float] = None
    vertical_accuracy: Optional[float] = None
    accuracy_units: Optional[str] = 'Feet'
    quality_code: Optional[str] = None
    is_control_point: Optional[bool] = False
    is_active: Optional[bool] = True
    attributes: Optional[Dict[str, Any]] = None


class SurveyPointUpdate(BaseModel):
    point_type: Optional[str] = None
    point_description: Optional[str] = None
    point_code: Optional[str] = None
    geometry: Optional[GeometryInput] = None
    northing: Optional[float] = None
    easting: Optional[float] = None
    elevation: Optional[float] = None
    survey_date: Optional[str] = None
    surveyed_by: Optional[str] = None
    survey_method: Optional[str] = None
    instrument_used: Optional[str] = None
    horizontal_accuracy: Optional[float] = None
    vertical_accuracy: Optional[float] = None
    accuracy_units: Optional[str] = None
    quality_code: Optional[str] = None
    is_control_point: Optional[bool] = None
    is_active: Optional[bool] = None
    attributes: Optional[Dict[str, Any]] = None


def _geom_expr(geojson_str: str, srid: int) -> str:
    """Return SQL expression to construct a PointZ geometry in SRID 2226 from provided GeoJSON and SRID."""
    return (
        "ST_Force3D("
        "CASE WHEN %s::int <> 2226 "
        "THEN ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(%s), %s::int), 2226) "
        "ELSE ST_SetSRID(ST_GeomFromGeoJSON(%s), 2226) END)"
    )


def _geom_expr_generic(geojson_placeholder: str, srid: int) -> str:
    """SRID-normalizing geometry expression to 2226, forcing 3D for any geometry type."""
    return (
        "ST_Force3D("
        "CASE WHEN %s::int <> 2226 "
        f"THEN ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON({geojson_placeholder}), %s::int), 2226) "
        f"ELSE ST_SetSRID(ST_GeomFromGeoJSON({geojson_placeholder}), 2226) END)"
    )


@router.get("/api/survey-points")
def list_survey_points(
    project_id: str = Query(...),
    search: Optional[str] = Query(None, description="Filter by point_number or description"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    try:
        filters = ["project_id = %s"]
        params: List[Any] = [project_id]
        if search:
            filters.append("(point_number ILIKE %s OR point_description ILIKE %s)")
            like = f"%{search}%"
            params.extend([like, like])

        where_clause = " AND ".join(filters)
        query = f"""
            SELECT 
              point_id, project_id, point_number, point_type, point_description,
              point_code, northing, easting, elevation,
              survey_date, surveyed_by, survey_method, instrument_used,
              horizontal_accuracy, vertical_accuracy, accuracy_units, quality_code,
              is_control_point, is_active,
              ST_AsGeoJSON(geometry)::json AS geometry,
              created_at, updated_at
            FROM survey_points
            WHERE {where_clause}
            ORDER BY point_number
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        rows = database.execute_query(query, tuple(params))
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list survey points: {str(e)}")


@router.get("/api/survey-points/{point_id}")
def get_survey_point(point_id: str):
    try:
        row = database.execute_single(
            """
            SELECT 
              point_id, project_id, point_number, point_type, point_description,
              point_code, northing, easting, elevation,
              survey_date, surveyed_by, survey_method, instrument_used,
              horizontal_accuracy, vertical_accuracy, accuracy_units, quality_code,
              is_control_point, is_active,
              ST_AsGeoJSON(geometry)::json AS geometry,
              created_at, updated_at
            FROM survey_points WHERE point_id = %s
            """,
            (point_id,)
        )
        if not row:
            raise HTTPException(status_code=404, detail="Survey point not found")
        return row
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get survey point: {str(e)}")


@router.post("/api/survey-points", status_code=201)
def create_survey_point(payload: SurveyPointCreate = Body(...)):
    try:
        geom_json = None
        srid = 2226
        if payload.geometry:
            geom_json = json.dumps(payload.geometry.geojson)
            srid = int(payload.geometry.srid or 2226)

        # Build base insert
        columns = [
            'project_id', 'point_number', 'point_type', 'point_description', 'point_code',
            'northing', 'easting', 'elevation', 'survey_date', 'surveyed_by', 'survey_method',
            'instrument_used', 'horizontal_accuracy', 'vertical_accuracy', 'accuracy_units',
            'quality_code', 'is_control_point', 'is_active'
        ]
        values = [
            payload.project_id, payload.point_number, payload.point_type, payload.point_description, payload.point_code,
            payload.northing, payload.easting, payload.elevation, payload.survey_date, payload.surveyed_by, payload.survey_method,
            payload.instrument_used, payload.horizontal_accuracy, payload.vertical_accuracy, payload.accuracy_units,
            payload.quality_code, payload.is_control_point, payload.is_active
        ]

        geom_sql = None
        geom_params: List[Any] = []
        if geom_json:
            geom_sql = _geom_expr('%s', srid)
            # For expression placeholders we need to pass parameters in order: srid, geojson, srid, geojson.
            geom_params = [srid, geom_json, srid, geom_json]
            columns.append('geometry')
        else:
            # Require geometry or NEZ
            if not (payload.northing is not None and payload.easting is not None and payload.elevation is not None):
                raise HTTPException(status_code=400, detail="Provide either geometry or northing/easting/elevation")
            # Build from NEZ as PointZ in SRID 2226
            geom_sql = 'ST_SetSRID(ST_MakePoint(%s, %s, %s), 2226)'
            geom_params = [payload.easting, payload.northing, payload.elevation]
            columns.append('geometry')

        placeholders = ','.join(['%s'] * len(values)) + ', ' + geom_sql
        insert_sql = f"INSERT INTO survey_points ({', '.join(columns)}) VALUES ({placeholders}) RETURNING point_id"

        point_row = database.execute_single(insert_sql, tuple(values + geom_params))
        point_id = point_row['point_id'] if point_row else None

        # Normalize NEZ from geometry if needed
        if point_id:
            database.execute_query(
                "UPDATE survey_points SET northing = ST_Y(geometry), easting = ST_X(geometry), elevation = ST_Z(geometry), updated_at = now() WHERE point_id = %s",
                (point_id,),
                fetch=False
            )

        # Return created
        created = database.execute_single(
            "SELECT point_id, project_id, point_number FROM survey_points WHERE point_id = %s",
            (point_id,)
        )
        return created or {"point_id": point_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create survey point: {str(e)}")


@router.put("/api/survey-points/{point_id}")
def update_survey_point(point_id: str, payload: SurveyPointUpdate = Body(...)):
    try:
        existing = database.execute_single("SELECT point_id FROM survey_points WHERE point_id = %s", (point_id,))
        if not existing:
            raise HTTPException(status_code=404, detail="Survey point not found")

        sets: List[str] = []
        params: List[Any] = []

        mapping = [
            ('point_type', payload.point_type),
            ('point_description', payload.point_description),
            ('point_code', payload.point_code),
            ('northing', payload.northing),
            ('easting', payload.easting),
            ('elevation', payload.elevation),
            ('survey_date', payload.survey_date),
            ('surveyed_by', payload.surveyed_by),
            ('survey_method', payload.survey_method),
            ('instrument_used', payload.instrument_used),
            ('horizontal_accuracy', payload.horizontal_accuracy),
            ('vertical_accuracy', payload.vertical_accuracy),
            ('accuracy_units', payload.accuracy_units),
            ('quality_code', payload.quality_code),
            ('is_control_point', payload.is_control_point),
            ('is_active', payload.is_active),
            ('attributes', json.dumps(payload.attributes) if payload.attributes is not None else None),
        ]
        for col, val in mapping:
            if val is not None:
                sets.append(f"{col} = %s")
                params.append(val)

        # Geometry update
        if payload.geometry is not None:
            geom_json = json.dumps(payload.geometry.geojson)
            srid = int(payload.geometry.srid or 2226)
            sets.append(f"geometry = {_geom_expr('%s', srid)}")
            params.extend([srid, geom_json, srid, geom_json])

        if not sets:
            return {"success": True}

        sets.append("updated_at = now()")
        params.append(point_id)
        sql = f"UPDATE survey_points SET {', '.join(sets)} WHERE point_id = %s"
        database.execute_query(sql, tuple(params), fetch=False)

        # Normalize NEZ from geometry when geometry updated
        if payload.geometry is not None:
            database.execute_query(
                "UPDATE survey_points SET northing = ST_Y(geometry), easting = ST_X(geometry), elevation = ST_Z(geometry) WHERE point_id = %s",
                (point_id,),
                fetch=False
            )
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update survey point: {str(e)}")


@router.delete("/api/survey-points/{point_id}")
def delete_survey_point(point_id: str):
    try:
        existing = database.execute_single("SELECT point_id FROM survey_points WHERE point_id = %s", (point_id,))
        if not existing:
            raise HTTPException(status_code=404, detail="Survey point not found")
        database.execute_query("DELETE FROM survey_points WHERE point_id = %s", (point_id,), fetch=False)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete survey point: {str(e)}")


# ============================================
# Bulk import: survey points from CSV
# ============================================

class SurveyPointsImportRequest(BaseModel):
    project_id: str
    csv_text: Optional[str] = Field(None, description="CSV content as text. Use this or file upload.")
    has_header: bool = True
    col_point_number: str = 'point_number'
    col_northing: str = 'northing'
    col_easting: str = 'easting'
    col_elevation: str = 'elevation'
    col_description: Optional[str] = 'point_description'


@router.post("/api/survey-points/import")
async def import_survey_points(
    payload: SurveyPointsImportRequest = Body(None),
    file: UploadFile = File(None)
):
    try:
        if not payload and not file:
            raise HTTPException(status_code=400, detail="Provide csv_text in body or upload a file")

        # Read CSV content
        if file is not None:
            content_bytes = await file.read()
            csv_text = content_bytes.decode('utf-8', errors='ignore')
            project_id = payload.project_id if payload else None
            has_header = payload.has_header if payload else True
            col_point_number = payload.col_point_number if payload else 'point_number'
            col_northing = payload.col_northing if payload else 'northing'
            col_easting = payload.col_easting if payload else 'easting'
            col_elevation = payload.col_elevation if payload else 'elevation'
            col_description = payload.col_description if payload else 'point_description'
        else:
            if not payload or not payload.csv_text:
                raise HTTPException(status_code=400, detail="csv_text is required when no file is uploaded")
            csv_text = payload.csv_text
            project_id = payload.project_id
            has_header = payload.has_header
            col_point_number = payload.col_point_number
            col_northing = payload.col_northing
            col_easting = payload.col_easting
            col_elevation = payload.col_elevation
            col_description = payload.col_description

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        reader = csv.DictReader(io.StringIO(csv_text)) if has_header else csv.reader(io.StringIO(csv_text))

        created = 0
        errors: List[str] = []
        if has_header:
            for i, row in enumerate(reader, start=1):
                try:
                    pn = str(row[col_point_number]).strip()
                    n = float(row[col_northing]) if row.get(col_northing) not in (None, '') else None
                    e = float(row[col_easting]) if row.get(col_easting) not in (None, '') else None
                    z = float(row[col_elevation]) if row.get(col_elevation) not in (None, '') else None
                    desc = str(row[col_description]).strip() if col_description and row.get(col_description) else None
                    if pn and n is not None and e is not None and z is not None:
                        insert_sql = (
                            "INSERT INTO survey_points (project_id, point_number, point_description, geometry) "
                            "VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s, %s), 2226)) "
                            "ON CONFLICT (project_id, point_number) DO UPDATE SET "
                            "point_description = EXCLUDED.point_description, geometry = EXCLUDED.geometry, updated_at = now()"
                        )
                        database.execute_query(insert_sql, (project_id, pn, desc, e, n, z), fetch=False)
                        # Normalize NEZ
                        database.execute_query(
                            "UPDATE survey_points SET northing = ST_Y(geometry), easting = ST_X(geometry), elevation = ST_Z(geometry) "
                            "WHERE project_id = %s AND point_number = %s",
                            (project_id, pn),
                            fetch=False
                        )
                        created += 1
                except Exception as ex:
                    errors.append(f"row {i}: {ex}")
        else:
            # No headers: assume [point_number,easting,northing,elevation,description?]
            for i, row in enumerate(reader, start=1):
                try:
                    pn = str(row[0]).strip()
                    e = float(row[1])
                    n = float(row[2])
                    z = float(row[3])
                    desc = str(row[4]).strip() if len(row) > 4 else None
                    insert_sql = (
                        "INSERT INTO survey_points (project_id, point_number, point_description, geometry) "
                        "VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s, %s), 2226)) "
                        "ON CONFLICT (project_id, point_number) DO UPDATE SET "
                        "point_description = EXCLUDED.point_description, geometry = EXCLUDED.geometry, updated_at = now()"
                    )
                    database.execute_query(insert_sql, (project_id, pn, desc, e, n, z), fetch=False)
                    database.execute_query(
                        "UPDATE survey_points SET northing = ST_Y(geometry), easting = ST_X(geometry), elevation = ST_Z(geometry) "
                        "WHERE project_id = %s AND point_number = %s",
                        (project_id, pn),
                        fetch=False
                    )
                    created += 1
                except Exception as ex:
                    errors.append(f"row {i}: {ex}")

        return {"imported": created, "errors": errors}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import survey points: {str(e)}")


# ============================================
# Utility lines
# ============================================

class UtilityLineCreate(BaseModel):
    project_id: str
    utility_type: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    diameter: Optional[str] = None
    material: Optional[str] = None
    geometry: GeometryInput


class UtilityLineUpdate(BaseModel):
    utility_type: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    diameter: Optional[str] = None
    material: Optional[str] = None
    geometry: Optional[GeometryInput] = None


@router.get("/api/utility-lines")
def list_utility_lines(
    project_id: str = Query(...),
    utility_type: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    try:
        filters = ["project_id = %s"]
        params: List[Any] = [project_id]
        if utility_type:
            filters.append("utility_type = %s")
            params.append(utility_type)
        if owner:
            filters.append("owner = %s")
            params.append(owner)

        query = f"""
            SELECT line_id, project_id, utility_type, owner, status, diameter, material,
                   ST_AsGeoJSON(geom)::json AS geometry
            FROM utility_lines
            WHERE {' AND '.join(filters)}
            ORDER BY utility_type, owner
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return database.execute_query(query, tuple(params))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list utility lines: {str(e)}")


@router.get("/api/utility-lines/{line_id}")
def get_utility_line(line_id: str):
    try:
        row = database.execute_single(
            "SELECT line_id, project_id, utility_type, owner, status, diameter, material, ST_AsGeoJSON(geom)::json AS geometry FROM utility_lines WHERE line_id = %s",
            (line_id,),
        )
        if not row:
            raise HTTPException(status_code=404, detail="Utility line not found")
        return row
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get utility line: {str(e)}")


@router.post("/api/utility-lines", status_code=201)
def create_utility_line(payload: UtilityLineCreate):
    try:
        geom_json = json.dumps(payload.geometry.geojson)
        srid = int(payload.geometry.srid or 2226)
        geom_sql = _geom_expr_generic('%s', srid)
        sql = (
            f"INSERT INTO utility_lines (project_id, utility_type, owner, status, diameter, material, geom) "
            f"VALUES (%s, %s, %s, %s, %s, %s, {geom_sql}) RETURNING line_id"
        )
        row = database.execute_single(sql, (payload.project_id, payload.utility_type, payload.owner, payload.status, payload.diameter, payload.material, srid, geom_json, srid, geom_json))
        return row or {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create utility line: {str(e)}")


@router.put("/api/utility-lines/{line_id}")
def update_utility_line(line_id: str, payload: UtilityLineUpdate):
    try:
        exists = database.execute_single("SELECT line_id FROM utility_lines WHERE line_id = %s", (line_id,))
        if not exists:
            raise HTTPException(status_code=404, detail="Utility line not found")
        sets: List[str] = []
        params: List[Any] = []
        for col, val in [
            ('utility_type', payload.utility_type),
            ('owner', payload.owner),
            ('status', payload.status),
            ('diameter', payload.diameter),
            ('material', payload.material),
        ]:
            if val is not None:
                sets.append(f"{col} = %s")
                params.append(val)
        if payload.geometry is not None:
            geom_json = json.dumps(payload.geometry.geojson)
            srid = int(payload.geometry.srid or 2226)
            sets.append(f"geom = {_geom_expr_generic('%s', srid)}")
            params.extend([srid, geom_json, srid, geom_json])
        if not sets:
            return {"success": True}
        params.append(line_id)
        sql = f"UPDATE utility_lines SET {', '.join(sets)} WHERE line_id = %s"
        database.execute_query(sql, tuple(params), fetch=False)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update utility line: {str(e)}")


@router.delete("/api/utility-lines/{line_id}")
def delete_utility_line(line_id: str):
    try:
        database.execute_query("DELETE FROM utility_lines WHERE line_id = %s", (line_id,), fetch=False)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete utility line: {str(e)}")


@router.get("/api/utility-lines/{line_id}/connectivity")
def get_utility_line_connectivity(line_id: str):
    try:
        rows = database.execute_query(
            "SELECT connectivity_id, node_a, node_b, connectivity FROM utility_network_connectivity WHERE line_id = %s",
            (line_id,),
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connectivity: {str(e)}")


# ============================================
# Parcels and Easements
# ============================================

class ParcelCreate(BaseModel):
    project_id: str
    apn: Optional[str] = None
    owner_name: Optional[str] = None
    situs_address: Optional[str] = None
    geometry: GeometryInput


class ParcelUpdate(BaseModel):
    apn: Optional[str] = None
    owner_name: Optional[str] = None
    situs_address: Optional[str] = None
    geometry: Optional[GeometryInput] = None


@router.get("/api/parcels")
def list_parcels(
    project_id: str = Query(...),
    search: Optional[str] = Query(None, description="APN or owner search"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    try:
        filters = ["project_id = %s"]
        params: List[Any] = [project_id]
        if search:
            filters.append("(apn ILIKE %s OR owner_name ILIKE %s)")
            like = f"%{search}%"
            params.extend([like, like])
        query = f"""
            SELECT parcel_id, project_id, apn, owner_name, situs_address,
                   area_sqft, ST_AsGeoJSON(geom)::json AS geometry
            FROM parcels
            WHERE {' AND '.join(filters)}
            ORDER BY apn NULLS LAST, owner_name
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return database.execute_query(query, tuple(params))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list parcels: {str(e)}")


@router.get("/api/parcels/{parcel_id}")
def get_parcel(parcel_id: str):
    try:
        row = database.execute_single(
            "SELECT parcel_id, project_id, apn, owner_name, situs_address, area_sqft, ST_AsGeoJSON(geom)::json AS geometry FROM parcels WHERE parcel_id = %s",
            (parcel_id,),
        )
        if not row:
            raise HTTPException(status_code=404, detail="Parcel not found")
        return row
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get parcel: {str(e)}")


@router.post("/api/parcels", status_code=201)
def create_parcel(payload: ParcelCreate):
    try:
        geom_json = json.dumps(payload.geometry.geojson)
        srid = int(payload.geometry.srid or 2226)
        geom_sql = _geom_expr_generic('%s', srid)
        sql = (
            f"INSERT INTO parcels (project_id, apn, owner_name, situs_address, geom, area_sqft) "
            f"VALUES (%s, %s, %s, %s, {geom_sql}, ST_Area({geom_sql})) RETURNING parcel_id"
        )
        params = (payload.project_id, payload.apn, payload.owner_name, payload.situs_address,
                  srid, geom_json, srid, geom_json, srid, geom_json, srid, geom_json)
        row = database.execute_single(sql, params)
        return row or {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create parcel: {str(e)}")


@router.put("/api/parcels/{parcel_id}")
def update_parcel(parcel_id: str, payload: ParcelUpdate):
    try:
        exists = database.execute_single("SELECT parcel_id FROM parcels WHERE parcel_id = %s", (parcel_id,))
        if not exists:
            raise HTTPException(status_code=404, detail="Parcel not found")
        sets: List[str] = []
        params: List[Any] = []
        for col, val in [
            ('apn', payload.apn),
            ('owner_name', payload.owner_name),
            ('situs_address', payload.situs_address),
        ]:
            if val is not None:
                sets.append(f"{col} = %s")
                params.append(val)
        if payload.geometry is not None:
            geom_json = json.dumps(payload.geometry.geojson)
            srid = int(payload.geometry.srid or 2226)
            sets.append(f"geom = {_geom_expr_generic('%s', srid)}")
            sets.append("area_sqft = ST_Area(geom)")
            params.extend([srid, geom_json, srid, geom_json])
        if not sets:
            return {"success": True}
        params.append(parcel_id)
        sql = f"UPDATE parcels SET {', '.join(sets)} WHERE parcel_id = %s"
        database.execute_query(sql, tuple(params), fetch=False)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update parcel: {str(e)}")


@router.delete("/api/parcels/{parcel_id}")
def delete_parcel(parcel_id: str):
    try:
        database.execute_query("DELETE FROM parcels WHERE parcel_id = %s", (parcel_id,), fetch=False)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete parcel: {str(e)}")


@router.get("/api/parcels/{parcel_id}/corners")
def get_parcel_corners(parcel_id: str):
    try:
        rows = database.execute_query(
            """
            SELECT pc.corner_id, pc.corner_type, pc.monument,
                   sp.point_number, sp.elevation,
                   ST_AsGeoJSON(sp.geometry)::json AS geometry
            FROM parcel_corners pc
            LEFT JOIN survey_points sp ON pc.survey_point_id = sp.point_id
            WHERE pc.parcel_id = %s
            ORDER BY pc.corner_type NULLS LAST, sp.point_number
            """,
            (parcel_id,),
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get parcel corners: {str(e)}")


@router.get("/api/easements")
def list_easements(project_id: str = Query(...), limit: int = 200, offset: int = 0):
    try:
        rows = database.execute_query(
            "SELECT easement_id, project_id, easement_type, purpose, ST_AsGeoJSON(geom)::json AS geometry FROM easements WHERE project_id = %s ORDER BY easement_type LIMIT %s OFFSET %s",
            (project_id, limit, offset),
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list easements: {str(e)}")


# ============================================
# Site features and Right-of-Way
# ============================================

@router.get("/api/site-trees")
def list_site_trees(project_id: str = Query(...), limit: int = 200, offset: int = 0):
    try:
        rows = database.execute_query(
            "SELECT tree_id, project_id, survey_point_id, species, dbh_in, condition, status, protection_status, notes FROM site_trees WHERE project_id = %s ORDER BY species NULLS LAST LIMIT %s OFFSET %s",
            (project_id, limit, offset),
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list site trees: {str(e)}")


@router.get("/api/utility-structures")
def list_utility_structures(
    project_id: str = Query(...),
    structure_type: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    limit: int = 200,
    offset: int = 0,
):
    try:
        filters = ["project_id = %s"]
        params: List[Any] = [project_id]
        if structure_type:
            filters.append("structure_type = %s")
            params.append(structure_type)
        if owner:
            filters.append("owner = %s")
            params.append(owner)
        query = f"""
            SELECT structure_id, project_id, survey_point_id, structure_type, owner, condition,
                   rim_elev, sump_depth, ground_elev, ST_AsGeoJSON(geom)::json AS geometry, metadata
            FROM utility_structures
            WHERE {' AND '.join(filters)}
            ORDER BY structure_type, owner
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return database.execute_query(query, tuple(params))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list utility structures: {str(e)}")


@router.get("/api/surface-features")
def list_surface_features(project_id: str = Query(...), feature_type: Optional[str] = None, limit: int = 200, offset: int = 0):
    try:
        filters = ["project_id = %s"]
        params: List[Any] = [project_id]
        if feature_type:
            filters.append("feature_type = %s")
            params.append(feature_type)
        query = f"""
            SELECT feature_id, project_id, drawing_id, feature_type, material, condition,
                   ST_AsGeoJSON(geom)::json AS geometry, metadata
            FROM surface_features
            WHERE {' AND '.join(filters)}
            ORDER BY feature_type
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return database.execute_query(query, tuple(params))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list surface features: {str(e)}")


@router.get("/api/right-of-way")
def list_right_of_way(project_id: str = Query(...), limit: int = 200, offset: int = 0):
    try:
        rows = database.execute_query(
            "SELECT row_id, project_id, jurisdiction, ST_AsGeoJSON(geom)::json AS geometry FROM right_of_way WHERE project_id = %s ORDER BY jurisdiction NULLS LAST LIMIT %s OFFSET %s",
            (project_id, limit, offset),
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list right-of-way: {str(e)}")


# ============================================
# Create/Update for Utility Structures, Surface Features, Right-of-Way
# ============================================

class UtilityStructureCreate(BaseModel):
    project_id: str
    survey_point_id: Optional[str] = None
    structure_type: Optional[str] = None
    owner: Optional[str] = None
    condition: Optional[str] = None
    rim_elev: Optional[float] = None
    sump_depth: Optional[float] = None
    ground_elev: Optional[float] = None
    geometry: Optional[GeometryInput] = None
    metadata: Optional[Dict[str, Any]] = None


class UtilityStructureUpdate(BaseModel):
    survey_point_id: Optional[str] = None
    structure_type: Optional[str] = None
    owner: Optional[str] = None
    condition: Optional[str] = None
    rim_elev: Optional[float] = None
    sump_depth: Optional[float] = None
    ground_elev: Optional[float] = None
    geometry: Optional[GeometryInput] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/api/utility-structures", status_code=201)
def create_utility_structure(payload: UtilityStructureCreate):
    try:
        cols = [
            'project_id', 'survey_point_id', 'structure_type', 'owner', 'condition',
            'rim_elev', 'sump_depth', 'ground_elev', 'metadata'
        ]
        vals: List[Any] = [
            payload.project_id, payload.survey_point_id, payload.structure_type, payload.owner, payload.condition,
            payload.rim_elev, payload.sump_depth, payload.ground_elev, Json(payload.metadata) if payload.metadata is not None else None
        ]

        geom_sql = None
        geom_params: List[Any] = []
        if payload.geometry is not None:
            geom_json = json.dumps(payload.geometry.geojson)
            srid = int(payload.geometry.srid or 2226)
            geom_sql = _geom_expr_generic('%s', srid)
            cols.append('geom')
            geom_params.extend([srid, geom_json, srid, geom_json])
        elif payload.survey_point_id:
            geom_sql = '(SELECT geometry FROM survey_points WHERE point_id = %s)'
            cols.append('geom')
            geom_params.append(payload.survey_point_id)

        placeholders = ','.join(['%s'] * len(vals))
        if geom_sql:
            placeholders = placeholders + ', ' + geom_sql
        sql = f"INSERT INTO utility_structures ({', '.join(cols)}) VALUES ({placeholders}) RETURNING structure_id"
        row = database.execute_single(sql, tuple(vals + geom_params))
        return row or {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create utility structure: {str(e)}")


@router.put("/api/utility-structures/{structure_id}")
def update_utility_structure(structure_id: str, payload: UtilityStructureUpdate):
    try:
        exists = database.execute_single("SELECT structure_id FROM utility_structures WHERE structure_id = %s", (structure_id,))
        if not exists:
            raise HTTPException(status_code=404, detail="Utility structure not found")
        sets: List[str] = []
        params: List[Any] = []
        for col, val in [
            ('survey_point_id', payload.survey_point_id),
            ('structure_type', payload.structure_type),
            ('owner', payload.owner),
            ('condition', payload.condition),
            ('rim_elev', payload.rim_elev),
            ('sump_depth', payload.sump_depth),
            ('ground_elev', payload.ground_elev),
        ]:
            if val is not None:
                sets.append(f"{col} = %s")
                params.append(val)
        if payload.metadata is not None:
            sets.append("metadata = %s::jsonb")
            params.append(json.dumps(payload.metadata))
        if payload.geometry is not None:
            geom_json = json.dumps(payload.geometry.geojson)
            srid = int(payload.geometry.srid or 2226)
            sets.append(f"geom = {_geom_expr_generic('%s', srid)}")
            params.extend([srid, geom_json, srid, geom_json])
        if not sets:
            return {"success": True}
        params.append(structure_id)
        sql = f"UPDATE utility_structures SET {', '.join(sets)} WHERE structure_id = %s"
        database.execute_query(sql, tuple(params), fetch=False)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update utility structure: {str(e)}")


@router.delete("/api/utility-structures/{structure_id}")
def delete_utility_structure(structure_id: str):
    try:
        database.execute_query("DELETE FROM utility_structures WHERE structure_id = %s", (structure_id,), fetch=False)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete utility structure: {str(e)}")


class SurfaceFeatureCreate(BaseModel):
    project_id: str
    drawing_id: Optional[str] = None
    feature_type: Optional[str] = None
    material: Optional[str] = None
    condition: Optional[str] = None
    geometry: GeometryInput
    metadata: Optional[Dict[str, Any]] = None


class SurfaceFeatureUpdate(BaseModel):
    drawing_id: Optional[str] = None
    feature_type: Optional[str] = None
    material: Optional[str] = None
    condition: Optional[str] = None
    geometry: Optional[GeometryInput] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/api/surface-features", status_code=201)
def create_surface_feature(payload: SurfaceFeatureCreate):
    try:
        geom_json = json.dumps(payload.geometry.geojson)
        srid = int(payload.geometry.srid or 2226)
        geom_sql = _geom_expr_generic('%s', srid)
        sql = (
            f"INSERT INTO surface_features (project_id, drawing_id, feature_type, material, condition, geom, metadata) "
            f"VALUES (%s, %s, %s, %s, %s, {geom_sql}, %s::jsonb) RETURNING feature_id"
        )
        row = database.execute_single(sql, (
            payload.project_id, payload.drawing_id, payload.feature_type, payload.material, payload.condition,
            srid, geom_json, srid, geom_json,
            json.dumps(payload.metadata) if payload.metadata is not None else None,
        ))
        return row or {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create surface feature: {str(e)}")


@router.put("/api/surface-features/{feature_id}")
def update_surface_feature(feature_id: str, payload: SurfaceFeatureUpdate):
    try:
        exists = database.execute_single("SELECT feature_id FROM surface_features WHERE feature_id = %s", (feature_id,))
        if not exists:
            raise HTTPException(status_code=404, detail="Surface feature not found")
        sets: List[str] = []
        params: List[Any] = []
        for col, val in [
            ('drawing_id', payload.drawing_id),
            ('feature_type', payload.feature_type),
            ('material', payload.material),
            ('condition', payload.condition),
        ]:
            if val is not None:
                sets.append(f"{col} = %s")
                params.append(val)
        if payload.metadata is not None:
            sets.append("metadata = %s::jsonb")
            params.append(json.dumps(payload.metadata))
        if payload.geometry is not None:
            geom_json = json.dumps(payload.geometry.geojson)
            srid = int(payload.geometry.srid or 2226)
            sets.append(f"geom = {_geom_expr_generic('%s', srid)}")
            params.extend([srid, geom_json, srid, geom_json])
        if not sets:
            return {"success": True}
        params.append(feature_id)
        sql = f"UPDATE surface_features SET {', '.join(sets)} WHERE feature_id = %s"
        database.execute_query(sql, tuple(params), fetch=False)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update surface feature: {str(e)}")


@router.delete("/api/surface-features/{feature_id}")
def delete_surface_feature(feature_id: str):
    try:
        database.execute_query("DELETE FROM surface_features WHERE feature_id = %s", (feature_id,), fetch=False)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete surface feature: {str(e)}")


class RightOfWayCreate(BaseModel):
    project_id: str
    jurisdiction: Optional[str] = None
    geometry: GeometryInput


class RightOfWayUpdate(BaseModel):
    jurisdiction: Optional[str] = None
    geometry: Optional[GeometryInput] = None


@router.post("/api/right-of-way", status_code=201)
def create_right_of_way(payload: RightOfWayCreate):
    try:
        geom_json = json.dumps(payload.geometry.geojson)
        srid = int(payload.geometry.srid or 2226)
        geom_sql = _geom_expr_generic('%s', srid)
        sql = f"INSERT INTO right_of_way (project_id, jurisdiction, geom) VALUES (%s, %s, {geom_sql}) RETURNING row_id"
        row = database.execute_single(sql, (payload.project_id, payload.jurisdiction, srid, geom_json, srid, geom_json))
        return row or {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create right-of-way: {str(e)}")


@router.put("/api/right-of-way/{row_id}")
def update_right_of_way(row_id: str, payload: RightOfWayUpdate):
    try:
        exists = database.execute_single("SELECT row_id FROM right_of_way WHERE row_id = %s", (row_id,))
        if not exists:
            raise HTTPException(status_code=404, detail="Right-of-way not found")
        sets: List[str] = []
        params: List[Any] = []
        if payload.jurisdiction is not None:
            sets.append("jurisdiction = %s")
            params.append(payload.jurisdiction)
        if payload.geometry is not None:
            geom_json = json.dumps(payload.geometry.geojson)
            srid = int(payload.geometry.srid or 2226)
            sets.append(f"geom = {_geom_expr_generic('%s', srid)}")
            params.extend([srid, geom_json, srid, geom_json])
        if not sets:
            return {"success": True}
        params.append(row_id)
        sql = f"UPDATE right_of_way SET {', '.join(sets)} WHERE row_id = %s"
        database.execute_query(sql, tuple(params), fetch=False)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update right-of-way: {str(e)}")


@router.delete("/api/right-of-way/{row_id}")
def delete_right_of_way(row_id: str):
    try:
        database.execute_query("DELETE FROM right_of_way WHERE row_id = %s", (row_id,), fetch=False)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete right-of-way: {str(e)}")


# ============================================
# Cross-sections and Earthwork
# ============================================

class CrossSectionCreate(BaseModel):
    station: float
    geometry: GeometryInput
    metadata: Optional[Dict[str, Any]] = None


@router.get("/api/alignments/{alignment_id}/cross-sections")
def list_cross_sections(alignment_id: str, limit: int = 500, offset: int = 0):
    try:
        rows = database.execute_query(
            "SELECT section_id, alignment_id, station, ST_AsGeoJSON(geom)::json AS geometry, metadata FROM cross_sections WHERE alignment_id = %s ORDER BY station LIMIT %s OFFSET %s",
            (alignment_id, limit, offset),
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list cross-sections: {str(e)}")


@router.post("/api/alignments/{alignment_id}/cross-sections", status_code=201)
def create_cross_section(alignment_id: str, payload: CrossSectionCreate):
    try:
        geom_json = json.dumps(payload.geometry.geojson)
        srid = int(payload.geometry.srid or 2226)
        geom_sql = _geom_expr_generic('%s', srid)
        sql = f"INSERT INTO cross_sections (alignment_id, station, geom, metadata) VALUES (%s, %s, {geom_sql}, %s) RETURNING section_id"
        row = database.execute_single(sql, (alignment_id, payload.station, srid, geom_json, srid, geom_json, json.dumps(payload.metadata) if payload.metadata is not None else None))
        return row or {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create cross-section: {str(e)}")


@router.get("/api/earthwork-quantities")
def list_earthwork_quantities(alignment_id: Optional[str] = None, project_id: Optional[str] = None, limit: int = 500, offset: int = 0):
    try:
        if alignment_id:
            rows = database.execute_query(
                "SELECT ew_id, alignment_id, station_start, station_end, cut_cy, fill_cy, metadata FROM earthwork_quantities WHERE alignment_id = %s ORDER BY station_start LIMIT %s OFFSET %s",
                (alignment_id, limit, offset),
            )
            return rows
        if project_id:
            rows = database.execute_query(
                """
                SELECT eq.ew_id, eq.alignment_id, a.name AS alignment_name, eq.station_start, eq.station_end, eq.cut_cy, eq.fill_cy, eq.metadata
                FROM earthwork_quantities eq
                JOIN alignments a ON eq.alignment_id = a.alignment_id
                WHERE a.project_id = %s
                ORDER BY a.name, eq.station_start
                LIMIT %s OFFSET %s
                """,
                (project_id, limit, offset),
            )
            return rows
        raise HTTPException(status_code=400, detail="Provide alignment_id or project_id")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list earthwork quantities: {str(e)}")


@router.get("/api/earthwork-balance/{alignment_id}")
def get_earthwork_balance(alignment_id: str, limit: int = 2000, offset: int = 0):
    try:
        rows = database.execute_query(
            "SELECT balance_id, alignment_id, station, cumulative_yardage FROM earthwork_balance WHERE alignment_id = %s ORDER BY station LIMIT %s OFFSET %s",
            (alignment_id, limit, offset),
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get earthwork balance: {str(e)}")


# ============================================
# Survey observations and traverse loops
# ============================================

class ObservationImportRequest(BaseModel):
    project_id: str
    csv_text: str
    has_header: bool = True
    col_session_id: str = 'session_id'
    col_station_point: str = 'station_point'
    col_backsight_point: str = 'backsight_point'
    col_target_point: str = 'target_point'
    col_time: str = 'observation_time'
    col_angle_dms: str = 'angle_dms'
    col_distance_ft: str = 'distance_ft'
    col_method: str = 'method'


def _resolve_point_id(project_id: str, point_ref: Optional[str]) -> Optional[str]:
    if not point_ref:
        return None
    # Resolve by explicit UUID or by point_number within project
    if len(point_ref) == 36 and '-' in point_ref:
        return point_ref
    row = database.execute_single(
        "SELECT point_id FROM survey_points WHERE project_id = %s AND point_number = %s",
        (project_id, point_ref),
    )
    return row['point_id'] if row else None


@router.get("/api/observations")
def list_observations(project_id: str = Query(...), session_id: Optional[str] = None, method: Optional[str] = None, limit: int = 500, offset: int = 0):
    try:
        filters = ["project_id = %s"]
        params: List[Any] = [project_id]
        if session_id:
            filters.append("session_id = %s")
            params.append(session_id)
        if method:
            filters.append("method = %s")
            params.append(method)
        query = f"""
            SELECT observation_id, project_id, session_id, instrument_station_point_id, backsight_point_id, target_point_id,
                   observation_time, angle_dms, distance_ft, method
            FROM survey_observations
            WHERE {' AND '.join(filters)}
            ORDER BY observation_time NULLS LAST
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return database.execute_query(query, tuple(params))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list observations: {str(e)}")


@router.post("/api/observations/import")
def import_observations(payload: ObservationImportRequest):
    try:
        reader = csv.DictReader(io.StringIO(payload.csv_text)) if payload.has_header else csv.reader(io.StringIO(payload.csv_text))
        created = 0
        errors: List[str] = []
        if payload.has_header:
            for i, row in enumerate(reader, start=1):
                try:
                    session_id = str(row.get(payload.col_session_id) or '').strip() or None
                    st_ref = str(row.get(payload.col_station_point) or '').strip() or None
                    bs_ref = str(row.get(payload.col_backsight_point) or '').strip() or None
                    tg_ref = str(row.get(payload.col_target_point) or '').strip() or None
                    tstamp = str(row.get(payload.col_time) or '').strip() or None
                    angle = str(row.get(payload.col_angle_dms) or '').strip() or None
                    dist = row.get(payload.col_distance_ft)
                    method = str(row.get(payload.col_method) or '').strip() or None
                    dist_ft = float(dist) if dist not in (None, '') else None
                    st_id = _resolve_point_id(payload.project_id, st_ref)
                    bs_id = _resolve_point_id(payload.project_id, bs_ref)
                    tg_id = _resolve_point_id(payload.project_id, tg_ref)
                    sql = (
                        "INSERT INTO survey_observations (project_id, session_id, instrument_station_point_id, backsight_point_id, target_point_id, observation_time, angle_dms, distance_ft, method, raw) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    )
                    raw_json = json.dumps(row)
                    database.execute_query(sql, (payload.project_id, session_id, st_id, bs_id, tg_id, tstamp, angle, dist_ft, method, raw_json), fetch=False)
                    created += 1
                except Exception as ex:
                    errors.append(f"row {i}: {ex}")
        else:
            for i, row in enumerate(reader, start=1):
                try:
                    # Assume [session, station_point, backsight_point, target_point, time, angle_dms, distance_ft, method]
                    session_id, st_ref, bs_ref, tg_ref, tstamp, angle, dist, method = (row + [None] * 8)[:8]
                    dist_ft = float(dist) if dist not in (None, '') else None
                    st_id = _resolve_point_id(payload.project_id, st_ref)
                    bs_id = _resolve_point_id(payload.project_id, bs_ref)
                    tg_id = _resolve_point_id(payload.project_id, tg_ref)
                    raw_json = json.dumps({"row": row})
                    sql = (
                        "INSERT INTO survey_observations (project_id, session_id, instrument_station_point_id, backsight_point_id, target_point_id, observation_time, angle_dms, distance_ft, method, raw) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    )
                    database.execute_query(sql, (payload.project_id, session_id, st_id, bs_id, tg_id, tstamp, angle, dist_ft, method, raw_json), fetch=False)
                    created += 1
                except Exception as ex:
                    errors.append(f"row {i}: {ex}")
        return {"imported": created, "errors": errors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import observations: {str(e)}")


@router.get("/api/traverse-loops")
def list_traverse_loops(project_id: str = Query(...), limit: int = 200, offset: int = 0):
    try:
        rows = database.execute_query(
            "SELECT loop_id, project_id, name, closure_ratio, misclosure, status FROM traverse_loops WHERE project_id = %s ORDER BY name LIMIT %s OFFSET %s",
            (project_id, limit, offset),
        )
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list traverse loops: {str(e)}")
