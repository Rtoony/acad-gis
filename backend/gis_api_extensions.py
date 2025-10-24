"""
Optional GIS API extensions for ACAD-GIS.

Routes are registered behind ``/api/gis`` and only become fully functional
when QGIS Python bindings are available. The goal is to keep the main server
backwards compatible while providing a surface area for GIS workflows.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

try:
    from qgis.core import QgsApplication  # type: ignore

    GIS_ENABLED = True
except Exception:  # pragma: no cover - absence of QGIS expected in dev
    QgsApplication = None  # type: ignore
    GIS_ENABLED = False

from gis_processor import get_processor  # noqa: E402  (local import)

router = APIRouter(prefix="/api/gis", tags=["GIS"])


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _build_database_url() -> Optional[str]:
    dsn = os.getenv("DATABASE_URL")
    if dsn:
        return dsn

    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    dbname = os.getenv("DB_NAME", "postgres")
    port = os.getenv("DB_PORT", "5432")

    if host and user and password:
        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    return None


def _require_gis():
    if not GIS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="GIS processing is disabled (QGIS bindings not available).",
        )


# --------------------------------------------------------------------------- #
# Pydantic models (minimal scaffolding – expand as feature work progresses)
# --------------------------------------------------------------------------- #


class LayerRef(BaseModel):
    table: str = Field(..., description="Database table containing geometry.")
    geom: str = Field("geom", description="Geometry column name.")
    srid: Optional[int] = Field(None, description="Override SRID if required.")
    where: Optional[str] = Field(None, description="Optional filtering clause.")


class BufferRequest(BaseModel):
    input: LayerRef
    distance: float
    dissolve: bool = False
    output_srid: Optional[int] = None


class ClipRequest(BaseModel):
    input: LayerRef
    clip: LayerRef


class IntersectionRequest(BaseModel):
    a: LayerRef
    b: LayerRef


class DissolveRequest(BaseModel):
    input: LayerRef
    by: Optional[List[str]] = None


class ReprojectRequest(BaseModel):
    input: LayerRef
    target_srid: int


class SpatialJoinRequest(BaseModel):
    left: LayerRef
    right: LayerRef
    how: str = Field("inner", description="Join type: inner|left.")
    predicate: str = Field(
        "intersects",
        description="Spatial predicate (intersects|contains|within|touches).",
    )


class ExportRequest(BaseModel):
    input: LayerRef
    filename: str


# Simple in-memory job store placeholder
_JOBS: Dict[str, Dict[str, Any]] = {}


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #


@router.get("/status")
def gis_status() -> Dict[str, Any]:
    return {"gis_enabled": GIS_ENABLED}


@router.get("/algorithms")
def gis_algorithms() -> Dict[str, Any]:
    if not GIS_ENABLED:
        # Keep the endpoint discoverable even when disabled.
        return {"total": 0, "algorithms": []}

    # TODO: integrate with QGIS processing registry to enumerate algorithms.
    return {"total": 0, "algorithms": []}


@router.post("/buffer")
def gis_buffer(req: BufferRequest) -> Dict[str, Any]:
    _require_gis()
    processor = get_processor(_build_database_url())
    if processor is None:
        raise HTTPException(status_code=500, detail="Failed to initialise QGIS.")

    # TODO: add real processing call
    return {"ok": True, "message": "Buffer submitted", "request": req}


@router.post("/clip")
def gis_clip(req: ClipRequest) -> Dict[str, Any]:
    _require_gis()
    return {"ok": True, "message": "Clip submitted", "request": req}


@router.post("/intersection")
def gis_intersection(req: IntersectionRequest) -> Dict[str, Any]:
    _require_gis()
    return {"ok": True, "message": "Intersection submitted", "request": req}


@router.post("/dissolve")
def gis_dissolve(req: DissolveRequest) -> Dict[str, Any]:
    _require_gis()
    return {"ok": True, "message": "Dissolve submitted", "request": req}


@router.post("/reproject")
def gis_reproject(req: ReprojectRequest) -> Dict[str, Any]:
    _require_gis()
    return {"ok": True, "message": "Reproject submitted", "request": req}


@router.post("/spatial-join")
def gis_spatial_join(req: SpatialJoinRequest) -> Dict[str, Any]:
    _require_gis()
    return {"ok": True, "message": "Spatial join submitted", "request": req}


@router.post("/export/shapefile")
def gis_export_shapefile(req: ExportRequest) -> Dict[str, Any]:
    _require_gis()
    return {"ok": True, "message": "Export (Shapefile) submitted", "request": req}


@router.post("/export/geojson")
def gis_export_geojson(req: ExportRequest) -> Dict[str, Any]:
    _require_gis()
    return {"ok": True, "message": "Export (GeoJSON) submitted", "request": req}


@router.get("/jobs/{job_id}")
def gis_job(job_id: str) -> Dict[str, Any]:
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs")
def gis_jobs() -> Dict[str, Any]:
    jobs = list(_JOBS.values())
    return {"total": len(jobs), "jobs": jobs}
