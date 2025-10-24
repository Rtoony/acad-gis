# QGIS Integration Quick Start Guide

## 🚀 Overview

This guide will get you up and running with QGIS-powered GIS operations in ACAD=GIS.

---

## 📋 Prerequisites

### 1. Install QGIS

**Windows (Recommended: OSGeo4W):**
```
Download OSGeo4W installer from: https://qgis.org/en/site/forusers/download.html
Run installer and select:
  - QGIS Desktop
  - GDAL
  - Python packages
Install to: C:\OSGeo4W64 (default)
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install qgis python3-qgis
```

**macOS:**
```bash
brew install qgis
```

### 2. Install Python Dependencies

```bash
pip install --break-system-packages ezdxf pyproj psycopg2-binary python-dotenv
```

---

## 🏃 Quick Start

### Step 1: Place Files in Your Project

Copy these new files to your project directory:

```
your-project/
├── gis_processor.py         ← Core QGIS integration
├── gis_api_extensions.py    ← API endpoints
├── start_qgis_server.bat    ← Windows launcher
├── start_qgis_server.sh     ← Linux/Mac launcher
├── api_server.py            ← (existing - needs updates)
└── database.py              ← (existing)
```

### Step 2: Update api_server.py

Add this import near the top of `api_server.py`:

```python
# Add after other imports
from gis_api_extensions import *
```

Add this to the startup section (in `if __name__ == "__main__"`):

```python
if __name__ == "__main__":
    print("🚀 Starting ACAD=GIS Enhanced API Server...")
    
    # Add GIS status check
    if GIS_ENABLED:
        print("✅ GIS Processing: ENABLED")
    else:
        print("⚠️  GIS Processing: DISABLED (QGIS not configured)")
    
    print("📡 Server running at: http://localhost:8000")
    print("📖 API Docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 3: Launch the Server

**Windows:**
```
Double-click: start_qgis_server.bat
```

**Linux/macOS:**
```bash
chmod +x start_qgis_server.sh
./start_qgis_server.sh
```

### Step 4: Test GIS Functionality

Open your browser to: `http://localhost:8000/docs`

Try these endpoints:

1. **Check GIS Status:**
   - `GET /api/gis/status`
   - Should return `{"gis_enabled": true}`

2. **List Available Algorithms:**
   - `GET /api/gis/algorithms`
   - Returns 400+ QGIS processing algorithms

3. **Run a Buffer Operation:**
   ```json
   POST /api/gis/buffer
   {
     "source_table": "canonical_features",
     "distance": 100,
     "segments": 5,
     "dissolve": false
   }
   ```

---

## 🎯 Common Operations

### Buffer Features

Creates a buffer zone around features:

```python
# Via Python
from gis_processor import get_processor

processor = get_processor()
result = processor.buffer_features(
    source_table='pipes',
    distance=50,  # 50 feet
    segments=8,
    dissolve=True
)
print(f"Created buffer: {result['output_table']}")
```

```bash
# Via API
curl -X POST "http://localhost:8000/api/gis/buffer" \
  -H "Content-Type: application/json" \
  -d '{
    "source_table": "pipes",
    "distance": 50,
    "segments": 8,
    "dissolve": true
  }'
```

### Clip Features

Extract features within a boundary:

```python
processor.clip_layer(
    input_table='site_features',
    clip_table='project_boundary',
    output_table='clipped_features'
)
```

### Spatial Join

Join attributes based on spatial relationship:

```python
processor.spatial_join(
    target_table='parcels',
    join_table='zoning_districts',
    predicate='intersects'
)
```

### Coordinate System Transformation

Reproject layers to different coordinate systems:

```python
processor.reproject_layer(
    input_table='survey_points',
    target_crs=3857,  # Web Mercator
    output_table='survey_points_web'
)
```

---

## 🗺️ Integration with Existing Workflows

### After DXF Import

Automatically process imported CAD data:

```python
# In import_dxf_georef.py
from gis_processor import get_processor

# After import completes...
if drawing['is_georeferenced']:
    processor = get_processor()
    
    # Create 50' buffer around utilities
    processor.buffer_features(
        source_table='canonical_features',
        distance=50,
        output_table=f'{drawing_id}_utilities_buffer'
    )
```

### Clash Detection

Find conflicts between utilities and proposed work:

```python
processor.intersection(
    layer1_table='existing_utilities',
    layer2_table='proposed_excavation',
    output_table='utility_conflicts'
)
```

### Site Boundary Extraction

Extract features within project limits:

```python
processor.clip_layer(
    input_table='city_infrastructure',
    clip_table='project_boundary',
    output_table='site_infrastructure'
)
```

---

## 📊 Available Operations

| Operation | Description | Use Case |
|-----------|-------------|----------|
| **buffer** | Create zones around features | Setbacks, clearances, service areas |
| **clip** | Extract features within boundary | Site extraction from regional data |
| **intersection** | Find overlapping features | Conflict detection, zoning analysis |
| **union** | Combine multiple layers | Merge site areas, combine utilities |
| **dissolve** | Merge features by attribute | Simplify boundaries, group parcels |
| **spatial_join** | Join attributes by location | Add zoning to parcels, assign districts |
| **reproject** | Change coordinate system | Convert State Plane to Web Mercator |
| **export** | Export to various formats | Create Shapefiles, GeoJSON, KML |

---

## 🔧 Troubleshooting

### "QGIS not available" Error

**Windows:**
- Check QGIS is installed at `C:\OSGeo4W64`
- Run `start_qgis_server.bat` to see detailed error
- Verify paths in the batch file

**Linux:**
- Install: `sudo apt install qgis python3-qgis`
- Check: `python3 -c "from qgis.core import QgsApplication"`

**macOS:**
- Install: `brew install qgis`
- Check installation at `/Applications/QGIS.app`

### "Layer not found" Error

- Ensure table exists in PostGIS database
- Check table has geometry column named 'geom' or 'geometry'
- Verify user has access to the table

### Slow Operations

- Add spatial indexes: `CREATE INDEX idx_geom ON table USING GIST(geom)`
- Simplify geometries before processing
- Use smaller buffer segments (e.g., 5 instead of 16)
- Process in chunks for large datasets

### Memory Issues

- Close other applications
- Process smaller areas at a time
- Increase system swap space
- Use server with more RAM for large projects

---

## 📚 Next Steps

1. **Explore Algorithms:**
   - Check `/api/gis/algorithms` for 400+ operations
   - Search by keyword (e.g., "slope", "contour", "network")

2. **Create Custom Workflows:**
   - Chain operations together
   - Automate common tasks
   - Build project-specific tools

3. **Frontend Integration:**
   - Add GIS tool UI to `tool_launcher.html`
   - Create visual parameter inputs
   - Display results on map

4. **Advanced Features:**
   - 3D analysis (terrain, viewsheds)
   - Network analysis (routing, service areas)
   - Raster processing (DEM analysis, interpolation)

---

## 🆘 Support

**Documentation:**
- Full plan: `QGIS_INTEGRATION_PLAN.md`
- QGIS docs: https://docs.qgis.org/latest/en/docs/

**Common Questions:**

**Q: Can I use this without QGIS installed?**
A: No, QGIS must be installed. The system gracefully disables GIS features if QGIS is not available.

**Q: Will this work on a server?**
A: Yes! QGIS runs in headless mode (no GUI), perfect for servers.

**Q: Can I process large datasets?**
A: Yes, but add spatial indexes and consider chunking very large datasets.

**Q: What coordinate systems are supported?**
A: All coordinate systems supported by QGIS/GDAL (thousands).

---

## ✅ Success Checklist

- [ ] QGIS installed
- [ ] Python dependencies installed
- [ ] Files copied to project
- [ ] api_server.py updated
- [ ] Server launches without errors
- [ ] `/api/gis/status` returns enabled
- [ ] Can list algorithms
- [ ] Buffer operation works
- [ ] Results visible in database

---

**Ready to go!** Start with simple operations like buffers and clips, then explore the 400+ available algorithms.

Happy GIS processing! 🗺️✨
