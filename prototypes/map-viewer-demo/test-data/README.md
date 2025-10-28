# Test Data Files

This directory contains sample files for testing the import functionality of the Map Viewer prototype.

## 📁 Files Included

### `sample_locations.csv`
- **Format:** CSV (Comma-Separated Values)
- **Features:** 10 San Francisco tourist locations
- **Columns:** name, latitude, longitude, type, description, year
- **Use Case:** Test CSV import with lat/lon columns

### `sample_landmarks.kml`
- **Format:** KML (Keyhole Markup Language)
- **Features:** 5 San Francisco landmarks
- **Use Case:** Test KML import from Google Earth format

## 🧪 How to Test Import

### Method 1: Drag and Drop
1. Start the map viewer (`python app.py`)
2. Open http://localhost:5000 in your browser
3. Click "Import Data" in the left control panel
4. Drag one of these files into the upload zone
5. The file will be processed and appear on the map

### Method 2: Click to Browse
1. Start the map viewer
2. Click "Import Data" in the left panel
3. Click anywhere in the upload zone
4. Select a file from this directory
5. The file will upload and display

## ✅ Expected Results

### CSV Import (`sample_locations.csv`)
- **Result:** 10 point markers on the map
- **Location:** San Francisco area
- **Properties:** All CSV columns will be in the popup (name, type, description, year)
- **Layer Name:** "sample_locations"

### KML Import (`sample_landmarks.kml`)
- **Result:** 5 point markers on the map
- **Location:** San Francisco landmarks
- **Properties:** Name and description in the popup
- **Layer Name:** "sample_landmarks"

## 🔍 What to Check

After uploading:
- ✅ Green success message appears
- ✅ New layer appears in "Data Layers" section
- ✅ Markers appear on the map
- ✅ Map automatically zooms to show all features
- ✅ Clicking markers shows popup with details
- ✅ Layer can be toggled on/off
- ✅ Layer can be exported in any format

## 📤 Testing Export

After importing a file:
1. Click "Tools" → "Export"
2. Select the uploaded layer from dropdown
3. Try exporting as:
   - **GeoJSON** - Original data in GeoJSON format
   - **KML** - Convert back to KML
   - **CSV** - Export as CSV (points only)
   - **PNG** - Image of current map view

## 🎓 Creating Your Own Test Files

### CSV File Requirements:
- Must have columns for coordinates (any of these work):
  - `latitude, longitude`
  - `lat, lon`
  - `y, x`
  - `northing, easting`
- All other columns become feature properties
- Header row is required

### CSV Example:
```csv
name,latitude,longitude,category,notes
Location 1,37.7749,-122.4194,Type A,Some notes
Location 2,37.7849,-122.4294,Type B,More notes
```

### KML File Requirements:
- Standard KML 2.2 format
- Must have `<Placemark>` elements
- Each placemark needs `<Point><coordinates>` for point features
- Format: `longitude,latitude,altitude`

### KML Example:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>My Location</name>
      <Point>
        <coordinates>-122.4194,37.7749,0</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
```

## 🐛 Troubleshooting

### CSV Import Fails
- **Error:** "Could not find latitude/longitude columns"
  - **Fix:** Ensure your CSV has columns named latitude/longitude (or lat/lon, y/x)
  - Check column names are in the header row

- **Error:** "No valid features found"
  - **Fix:** Ensure latitude/longitude values are numbers, not text
  - Check for proper decimal format (37.7749, not 37° 46' 29.64")

### KML Import Fails
- **Error:** "No valid features found"
  - **Fix:** Ensure your KML has `<Point>` elements with `<coordinates>`
  - LineString and Polygon support may vary depending on complexity

### General Issues
- **File not uploading:** Check file size is under 50MB
- **Nothing happens:** Check browser console (F12) for errors
- **Wrong location:** Verify longitude is negative for Western Hemisphere

## 📝 Notes

- Both files contain locations in San Francisco (longitude ~-122.4, latitude ~37.8)
- Files are small and load instantly
- Perfect for quick testing of import/export workflow
- Use these as templates for creating your own test data

---

**Happy Testing!** 🗺️
