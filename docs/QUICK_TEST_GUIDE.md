# Project Map - Quick Test Guide

## 🚀 5-Minute Test

### Step 1: Start API Server
```bash
cd H:\acad-gis
python backend/api_server.py
```
✅ Look for: `Server running at: http://localhost:8000`

### Step 2: Test API
Open in browser:
```
http://localhost:8000/api/projects/e9e2715f-6624-432d-a11b-8a8e3e3582ed/features
```
✅ Should see: GeoJSON with 3 features

### Step 3: Open Tool Launcher
Double-click: `H:\acad-gis\tool_launcher.html`

✅ Look for: **Project Map** card (teal color, "New" badge)

### Step 4: Click Project Map Card
✅ Should open: `frontend/tools/project-map.html`

### Step 5: Select Project
1. Click project dropdown
2. Select "Santa Rosa Demo A"
3. Wait for map to load

✅ Should see:
- Map zooms to Santa Rosa, CA
- 3 layer toggles appear
- Features display on map
- Coordinate display at bottom

### Step 6: Interact
- Click layer toggles (QA_POINT, QA_LINE, QA_AREA)
- Click features to see popups
- Click "Zoom to Extent" button
- Move mouse to see coordinates

---

## ✅ Success Criteria

| Test | Expected Result |
|------|----------------|
| API Health | `http://localhost:8000/api/health` shows "ok" |
| Features Load | GeoJSON with 3 features |
| Map Centers | ~38.4°N, ~122.7°W (Santa Rosa) |
| Layer Toggles | 3 toggles visible |
| Feature Count | "3 features loaded" |
| Popup | Click feature shows type/layer/metadata |
| Coordinates | Update on mouse move |

---

## 🐛 Common Issues

### "API Offline"
```bash
# Restart server
cd H:\acad-gis
python backend/api_server.py
```

### No Features Display
Check browser console (F12 → Console tab)
Look for error messages

### Wrong Location
Verify coordinates in SQL:
```sql
SELECT
  feature_type,
  ST_X(geom) as lon,
  ST_Y(geom) as lat
FROM canonical_features
WHERE project_id = 'e9e2715f-6624-432d-a11b-8a8e3e3582ed';
```
Expect: lat ~38.4, lon ~-122.7

---

## 📊 Your Test Data

You have 3 Santa Rosa Demo projects with 9 total features:

| Project | Features | Types |
|---------|----------|-------|
| Santa Rosa Demo A | 3 | Point, Line, Polygon |
| Santa Rosa Demo B | 3 | Point, Line, Polygon |
| Santa Rosa Demo C | 3 | Point, Line, Polygon |

All features are QA test data in Sonoma County, CA.

---

## 🎯 What This Tests

✅ Database connection (Supabase)
✅ PostGIS geometry → GeoJSON conversion
✅ Coordinate transformation (EPSG:2226 → 4326)
✅ Backend API endpoints
✅ Frontend React components
✅ Leaflet map integration
✅ Layer controls
✅ Feature styling
✅ Popups and interactivity

---

## 🔄 Next: Add Real Data

Once this works, import real project data:
1. DXF files with coordinate system
2. Will populate `canonical_features` table
3. Appear automatically in Project Map

See `PROJECT_MAP_INTEGRATION.md` for full details.
