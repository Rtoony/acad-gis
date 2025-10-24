"""
API Server Extensions for GIS Operations
Add these routes to api_server.py

This module provides FastAPI endpoints for QGIS processing operations.
"""

from fastapi import BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime

# Import GIS processor
try:
    from gis_processor import get_processor, check_qgis_available
    GIS_ENABLED = check_qgis_available()
except ImportError:
    GIS_ENABLED = False
    print("⚠️  GIS processor not available")


# ============================================
# PYDANTIC MODELS FOR GIS OPERATIONS
# ============================================

class BufferParams(BaseModel):
    """Parameters for buffer operation."""
    source_table: str
    distance: float
    segments: int = 5
    dissolve: bool = False
    output_table: Optional[str] = None


class ClipParams(BaseModel):
    """Parameters for clip operation."""
    input_table: str
    clip_table: str
    output_table: Optional[str] = None


class IntersectionParams(BaseModel):
    """Parameters for intersection operation."""
    layer1_table: str
    layer2_table: str
    output_table: Optional[str] = None


class DissolveParams(BaseModel):
    """Parameters for dissolve operation."""
    input_table: str
    field: Optional[str] = None
    output_table: Optional[str] = None


class ReprojectParams(BaseModel):
    """Parameters for reprojection operation."""
    input_table: str
    target_crs: int
    output_table: Optional[str] = None


class SpatialJoinParams(BaseModel):
    """Parameters for spatial join operation."""
    target_table: str
    join_table: str
    predicate: str = 'intersects'
    output_table: Optional[str] = None


class ExportParams(BaseModel):
    """Parameters for export operations."""
    input_table: str
    format: str  # 'shapefile', 'geojson', 'kml', 'dxf'
    output_path: Optional[str] = None


class GISJobResponse(BaseModel):
    """Response model for GIS job creation."""
    job_id: str
    status: str
    message: str


class GISJobStatus(BaseModel):
    """Status model for GIS job."""
    job_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    operation: str
    progress: int
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


# ============================================
# JOB MANAGEMENT (SIMPLE IN-MEMORY FOR NOW)
# ============================================

# In production, this should be in database
GIS_JOBS: Dict[str, GISJobStatus] = {}


def create_gis_job(operation: str, params: Dict[str, Any]) -> str:
    """Create a new GIS job and return job ID."""
    job_id = str(uuid.uuid4())
    
    GIS_JOBS[job_id] = GISJobStatus(
        job_id=job_id,
        status='pending',
        operation=operation,
        progress=0,
        created_at=datetime.now().isoformat()
    )
    
    return job_id


def update_gis_job(job_id: str, 
                   status: str = None,
                   progress: int = None,
                   result: Dict = None,
                   error: str = None):
    """Update GIS job status."""
    if job_id not in GIS_JOBS:
        return
    
    job = GIS_JOBS[job_id]
    
    if status:
        job.status = status
    if progress is not None:
        job.progress = progress
    if result:
        job.result = result
    if error:
        job.error_message = error
    
    if status in ['completed', 'failed']:
        job.completed_at = datetime.now().isoformat()


def get_gis_job(job_id: str) -> Optional[GISJobStatus]:
    """Get GIS job status."""
    return GIS_JOBS.get(job_id)


# ============================================
# BACKGROUND TASK EXECUTORS
# ============================================

async def execute_buffer_job(job_id: str, params: BufferParams):
    """Execute buffer operation in background."""
    try:
        update_gis_job(job_id, status='running', progress=10)
        
        processor = get_processor()
        if not processor:
            raise Exception("QGIS processor not available")
        
        update_gis_job(job_id, progress=30)
        
        result = processor.buffer_features(
            source_table=params.source_table,
            distance=params.distance,
            segments=params.segments,
            dissolve=params.dissolve,
            output_table=params.output_table
        )
        
        update_gis_job(job_id, status='completed', progress=100, result=result)
        
    except Exception as e:
        update_gis_job(job_id, status='failed', error=str(e))


async def execute_clip_job(job_id: str, params: ClipParams):
    """Execute clip operation in background."""
    try:
        update_gis_job(job_id, status='running', progress=10)
        
        processor = get_processor()
        if not processor:
            raise Exception("QGIS processor not available")
        
        update_gis_job(job_id, progress=30)
        
        result = processor.clip_layer(
            input_table=params.input_table,
            clip_table=params.clip_table,
            output_table=params.output_table
        )
        
        update_gis_job(job_id, status='completed', progress=100, result=result)
        
    except Exception as e:
        update_gis_job(job_id, status='failed', error=str(e))


async def execute_intersection_job(job_id: str, params: IntersectionParams):
    """Execute intersection operation in background."""
    try:
        update_gis_job(job_id, status='running', progress=10)
        
        processor = get_processor()
        if not processor:
            raise Exception("QGIS processor not available")
        
        update_gis_job(job_id, progress=30)
        
        result = processor.intersection(
            layer1_table=params.layer1_table,
            layer2_table=params.layer2_table,
            output_table=params.output_table
        )
        
        update_gis_job(job_id, status='completed', progress=100, result=result)
        
    except Exception as e:
        update_gis_job(job_id, status='failed', error=str(e))


# ============================================
# API ENDPOINTS (TO BE ADDED TO api_server.py)
# ============================================

"""
Add these endpoints to api_server.py:

# GIS Status Check
@app.get("/api/gis/status")
def gis_status():
    '''Check if GIS processing is available.'''
    return {
        "gis_enabled": GIS_ENABLED,
        "message": "GIS processing available" if GIS_ENABLED else "QGIS not configured"
    }


# List Available Algorithms
@app.get("/api/gis/algorithms")
def list_gis_algorithms(
    group: Optional[str] = None,
    search: Optional[str] = None
):
    '''List available QGIS algorithms.'''
    if not GIS_ENABLED:
        raise HTTPException(status_code=503, detail="GIS not available")
    
    processor = get_processor()
    algorithms = processor.list_algorithms(group=group, search=search)
    
    return {
        "total": len(algorithms),
        "algorithms": algorithms
    }


# Buffer Operation
@app.post("/api/gis/buffer", response_model=GISJobResponse)
async def create_buffer(
    params: BufferParams,
    background_tasks: BackgroundTasks
):
    '''Create buffer around features.'''
    if not GIS_ENABLED:
        raise HTTPException(status_code=503, detail="GIS not available")
    
    # Create job
    job_id = create_gis_job('buffer', params.dict())
    
    # Execute in background
    background_tasks.add_task(execute_buffer_job, job_id, params)
    
    return GISJobResponse(
        job_id=job_id,
        status='pending',
        message='Buffer operation queued'
    )


# Clip Operation
@app.post("/api/gis/clip", response_model=GISJobResponse)
async def create_clip(
    params: ClipParams,
    background_tasks: BackgroundTasks
):
    '''Clip features by boundary.'''
    if not GIS_ENABLED:
        raise HTTPException(status_code=503, detail="GIS not available")
    
    job_id = create_gis_job('clip', params.dict())
    background_tasks.add_task(execute_clip_job, job_id, params)
    
    return GISJobResponse(
        job_id=job_id,
        status='pending',
        message='Clip operation queued'
    )


# Intersection Operation
@app.post("/api/gis/intersection", response_model=GISJobResponse)
async def create_intersection(
    params: IntersectionParams,
    background_tasks: BackgroundTasks
):
    '''Find intersection between layers.'''
    if not GIS_ENABLED:
        raise HTTPException(status_code=503, detail="GIS not available")
    
    job_id = create_gis_job('intersection', params.dict())
    background_tasks.add_task(execute_intersection_job, job_id, params)
    
    return GISJobResponse(
        job_id=job_id,
        status='pending',
        message='Intersection operation queued'
    )


# Dissolve Operation
@app.post("/api/gis/dissolve", response_model=GISJobResponse)
async def create_dissolve(params: DissolveParams):
    '''Dissolve features by attribute.'''
    if not GIS_ENABLED:
        raise HTTPException(status_code=503, detail="GIS not available")
    
    try:
        processor = get_processor()
        result = processor.dissolve(
            input_table=params.input_table,
            field=params.field,
            output_table=params.output_table
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Reproject Operation
@app.post("/api/gis/reproject", response_model=GISJobResponse)
async def create_reproject(params: ReprojectParams):
    '''Reproject layer to different coordinate system.'''
    if not GIS_ENABLED:
        raise HTTPException(status_code=503, detail="GIS not available")
    
    try:
        processor = get_processor()
        result = processor.reproject_layer(
            input_table=params.input_table,
            target_crs=params.target_crs,
            output_table=params.output_table
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Spatial Join Operation
@app.post("/api/gis/spatial-join", response_model=GISJobResponse)
async def create_spatial_join(params: SpatialJoinParams):
    '''Perform spatial join between layers.'''
    if not GIS_ENABLED:
        raise HTTPException(status_code=503, detail="GIS not available")
    
    try:
        processor = get_processor()
        result = processor.spatial_join(
            target_table=params.target_table,
            join_table=params.join_table,
            predicate=params.predicate,
            output_table=params.output_table
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export to Shapefile
@app.post("/api/gis/export/shapefile")
async def export_shapefile(params: ExportParams):
    '''Export layer to Shapefile format.'''
    if not GIS_ENABLED:
        raise HTTPException(status_code=503, detail="GIS not available")
    
    try:
        processor = get_processor()
        
        # Generate output path if not provided
        output_path = params.output_path
        if not output_path:
            output_path = f"/tmp/{params.input_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.shp"
        
        result = processor.export_to_shapefile(
            input_table=params.input_table,
            output_path=output_path
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export to GeoJSON
@app.post("/api/gis/export/geojson")
async def export_geojson(params: ExportParams):
    '''Export layer to GeoJSON format.'''
    if not GIS_ENABLED:
        raise HTTPException(status_code=503, detail="GIS not available")
    
    try:
        processor = get_processor()
        
        # Generate output path if not provided
        output_path = params.output_path
        if not output_path:
            output_path = f"/tmp/{params.input_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.geojson"
        
        result = processor.export_to_geojson(
            input_table=params.input_table,
            output_path=output_path
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get Job Status
@app.get("/api/gis/jobs/{job_id}", response_model=GISJobStatus)
async def get_job_status(job_id: str):
    '''Get status of a GIS processing job.'''
    job = get_gis_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


# List All Jobs
@app.get("/api/gis/jobs")
async def list_jobs(
    status: Optional[str] = None,
    operation: Optional[str] = None,
    limit: int = 50
):
    '''List GIS processing jobs with optional filters.'''
    jobs = list(GIS_JOBS.values())
    
    # Filter by status
    if status:
        jobs = [j for j in jobs if j.status == status]
    
    # Filter by operation
    if operation:
        jobs = [j for j in jobs if j.operation == operation]
    
    # Sort by creation time (newest first)
    jobs.sort(key=lambda j: j.created_at, reverse=True)
    
    # Limit results
    jobs = jobs[:limit]
    
    return {
        "total": len(jobs),
        "jobs": jobs
    }

"""

# ============================================
# INTEGRATION INSTRUCTIONS
# ============================================

INTEGRATION_INSTRUCTIONS = """
TO INTEGRATE GIS OPERATIONS INTO api_server.py:

1. Add import at the top:
   ```python
   from gis_api_extensions import *
   ```

2. Copy all the endpoint definitions from the docstring above
   and paste them into api_server.py (after existing endpoints)

3. Update the startup message to show GIS status:
   ```python
   if __name__ == "__main__":
       print("🚀 Starting ACAD=GIS Enhanced API Server...")
       if GIS_ENABLED:
           print("✅ GIS Processing: ENABLED")
       else:
           print("⚠️  GIS Processing: DISABLED (QGIS not configured)")
       print("📡 Server running at: http://localhost:8000")
       print("📖 API Docs at: http://localhost:8000/docs")
       uvicorn.run(app, host="0.0.0.0", port=8000)
   ```

4. Test with:
   ```bash
   python api_server.py
   ```

5. Access interactive API docs at:
   http://localhost:8000/docs
   
6. Test GIS endpoints:
   - GET /api/gis/status
   - GET /api/gis/algorithms
   - POST /api/gis/buffer
   etc.
"""

if __name__ == "__main__":
    print(INTEGRATION_INSTRUCTIONS)
