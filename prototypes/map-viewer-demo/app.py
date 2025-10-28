"""
Flask Backend for Interactive Leaflet Map Demo
Provides API endpoints for map data layers and preset configurations
"""

from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
import os
import csv
import io
from pathlib import Path
from datetime import datetime

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
CORS(app)

# Configuration
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
UPLOAD_DIR = BASE_DIR / 'uploads'
CONFIG_FILE = BASE_DIR / 'config.json'
PRESETS_FILE = BASE_DIR / 'data' / 'presets.json'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'geojson', 'json', 'csv', 'kml', 'kmz'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Ensure upload directory exists
UPLOAD_DIR.mkdir(exist_ok=True)

# Load configuration
def load_config():
    """Load application configuration from config.json"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "map_center": [37.7749, -122.4194],
            "initial_zoom": 10,
            "company_name": "Engineering Solutions Inc.",
            "default_basemap": "osm"
        }

config = load_config()

@app.route('/')
def index():
    """Serve the main map viewer page"""
    return render_template('index.html', config=config)

@app.route('/api/config')
def get_config():
    """Get application configuration"""
    return jsonify(config)

@app.route('/api/layers')
def get_layers():
    """Return list of available data layers"""
    layers = []
    if DATA_DIR.exists():
        for file in DATA_DIR.glob('*.geojson'):
            layer_name = file.stem
            layers.append({
                'name': layer_name,
                'display_name': layer_name.replace('_', ' ').title(),
                'type': 'geojson',
                'url': f'/api/layer/{layer_name}'
            })
    return jsonify(layers)

@app.route('/api/layer/<layer_name>')
def get_layer(layer_name):
    """Get GeoJSON data for a specific layer"""
    try:
        file_path = DATA_DIR / f'{layer_name}.geojson'
        if not file_path.exists():
            return jsonify({'error': 'Layer not found'}), 404

        with open(file_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Get all saved preset configurations"""
    try:
        if PRESETS_FILE.exists():
            with open(PRESETS_FILE, 'r') as f:
                presets = json.load(f)
        else:
            # Return default presets
            presets = get_default_presets()
        return jsonify(presets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preset', methods=['POST'])
def save_preset():
    """Save a custom preset configuration"""
    try:
        preset_data = request.json

        # Load existing presets
        if PRESETS_FILE.exists():
            with open(PRESETS_FILE, 'r') as f:
                presets = json.load(f)
        else:
            presets = get_default_presets()

        # Add or update preset
        preset_name = preset_data.get('name')
        if not preset_name:
            return jsonify({'error': 'Preset name is required'}), 400

        presets[preset_name] = preset_data

        # Save to file
        with open(PRESETS_FILE, 'w') as f:
            json.dump(presets, f, indent=2)

        return jsonify({'success': True, 'message': f'Preset "{preset_name}" saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preset/<preset_name>', methods=['GET'])
def get_preset(preset_name):
    """Get a specific preset configuration"""
    try:
        if PRESETS_FILE.exists():
            with open(PRESETS_FILE, 'r') as f:
                presets = json.load(f)
        else:
            presets = get_default_presets()

        if preset_name not in presets:
            return jsonify({'error': 'Preset not found'}), 404

        return jsonify(presets[preset_name])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_default_presets():
    """Return default presentation presets"""
    return {
        "executive_overview": {
            "name": "Executive Overview",
            "description": "Clean satellite basemap, major projects only, large icons",
            "basemap": "satellite",
            "layers": ["projects"],
            "markerSize": "large",
            "showLabels": True,
            "fontSize": "large",
            "colorScheme": "brand",
            "basemapOpacity": 100,
            "layerOpacity": 90,
            "showLegend": True,
            "showScale": False
        },
        "detailed_technical": {
            "name": "Detailed Technical",
            "description": "Topographic basemap, all layers visible, detailed popups",
            "basemap": "terrain",
            "layers": ["projects", "service_areas", "active_sites", "infrastructure"],
            "markerSize": "medium",
            "showLabels": True,
            "fontSize": "medium",
            "colorScheme": "standard",
            "basemapOpacity": 100,
            "layerOpacity": 85,
            "showLegend": True,
            "showScale": True
        },
        "client_presentation": {
            "name": "Client Presentation",
            "description": "Professional grayscale basemap, selected projects highlighted",
            "basemap": "grayscale",
            "layers": ["projects", "service_areas"],
            "markerSize": "large",
            "showLabels": True,
            "fontSize": "medium",
            "colorScheme": "brand",
            "basemapOpacity": 80,
            "layerOpacity": 100,
            "showLegend": True,
            "showScale": False
        },
        "print_ready": {
            "name": "Print Ready",
            "description": "High contrast, clear labels, optimized for printing",
            "basemap": "grayscale",
            "layers": ["projects", "service_areas"],
            "markerSize": "large",
            "showLabels": True,
            "fontSize": "large",
            "colorScheme": "high_contrast",
            "basemapOpacity": 100,
            "layerOpacity": 100,
            "showLegend": True,
            "showScale": True
        },
        "minimal_modern": {
            "name": "Minimal Modern",
            "description": "Data-focused with minimal basemap, bold colors",
            "basemap": "light",
            "layers": ["projects", "active_sites"],
            "markerSize": "large",
            "showLabels": False,
            "fontSize": "medium",
            "colorScheme": "vibrant",
            "basemapOpacity": 40,
            "layerOpacity": 100,
            "showLegend": True,
            "showScale": False
        }
    }

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# ===================================
# Helper Functions
# ===================================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def csv_to_geojson(csv_file):
    """Convert CSV file to GeoJSON format"""
    try:
        # Read CSV
        csv_content = csv_file.read().decode('utf-8')
        csv_file.seek(0)  # Reset file pointer

        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)

        if not rows:
            return None, "CSV file is empty"

        # Try to find coordinate columns
        headers = list(rows[0].keys())
        lat_col = None
        lon_col = None

        # Common latitude column names
        lat_names = ['latitude', 'lat', 'y', 'northing', 'latitude_decimal']
        # Common longitude column names
        lon_names = ['longitude', 'lon', 'lng', 'x', 'easting', 'longitude_decimal']

        for header in headers:
            header_lower = header.lower().strip()
            if header_lower in lat_names and not lat_col:
                lat_col = header
            if header_lower in lon_names and not lon_col:
                lon_col = header

        if not lat_col or not lon_col:
            return None, f"Could not find latitude/longitude columns. Available columns: {', '.join(headers)}"

        # Build GeoJSON
        features = []
        for row in rows:
            try:
                lat = float(row[lat_col])
                lon = float(row[lon_col])

                # Create properties (all columns except coordinates)
                properties = {k: v for k, v in row.items() if k not in [lat_col, lon_col]}

                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": properties
                }
                features.append(feature)
            except (ValueError, KeyError) as e:
                continue  # Skip invalid rows

        if not features:
            return None, "No valid features found in CSV"

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        return geojson, None
    except Exception as e:
        return None, f"Error parsing CSV: {str(e)}"

def kml_to_geojson(kml_content):
    """Convert KML to GeoJSON format (simplified parser)"""
    try:
        # Try using geopandas if available
        try:
            import geopandas as gpd
            import tempfile

            # Write KML to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.kml', delete=False) as tmp:
                tmp.write(kml_content)
                tmp_path = tmp.name

            # Read with geopandas
            gdf = gpd.read_file(tmp_path, driver='KML')

            # Clean up temp file
            os.unlink(tmp_path)

            # Convert to GeoJSON
            geojson = json.loads(gdf.to_json())
            return geojson, None

        except ImportError:
            # Fallback to basic XML parsing if geopandas not available
            import xml.etree.ElementTree as ET

            # Parse KML
            root = ET.fromstring(kml_content)

            # KML namespace
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}

            features = []

            # Find all Placemarks
            for placemark in root.findall('.//kml:Placemark', ns):
                name_elem = placemark.find('kml:name', ns)
                name = name_elem.text if name_elem is not None else "Unnamed"

                # Try to find Point coordinates
                point = placemark.find('.//kml:Point/kml:coordinates', ns)
                if point is not None:
                    coords_text = point.text.strip()
                    coords = coords_text.split(',')
                    if len(coords) >= 2:
                        feature = {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [float(coords[0]), float(coords[1])]
                            },
                            "properties": {"name": name}
                        }
                        features.append(feature)

            if not features:
                return None, "No valid features found in KML"

            geojson = {
                "type": "FeatureCollection",
                "features": features
            }

            return geojson, None

    except Exception as e:
        return None, f"Error parsing KML: {str(e)}"

# ===================================
# Import Endpoints
# ===================================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads (CSV, KML, GeoJSON)"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

        # Secure filename
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"

        # Process based on file type
        if file_ext in ['geojson', 'json']:
            # Read and validate GeoJSON
            content = file.read().decode('utf-8')
            geojson = json.loads(content)

            if 'type' not in geojson or geojson['type'] != 'FeatureCollection':
                return jsonify({'error': 'Invalid GeoJSON format'}), 400

            layer_name = filename.rsplit('.', 1)[0]

        elif file_ext == 'csv':
            # Convert CSV to GeoJSON
            geojson, error = csv_to_geojson(file)
            if error:
                return jsonify({'error': error}), 400

            layer_name = filename.rsplit('.', 1)[0]

        elif file_ext in ['kml', 'kmz']:
            # Convert KML to GeoJSON
            content = file.read().decode('utf-8')
            geojson, error = kml_to_geojson(content)
            if error:
                return jsonify({'error': error}), 400

            layer_name = filename.rsplit('.', 1)[0]

        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        # Return GeoJSON data
        return jsonify({
            'success': True,
            'layer_name': layer_name,
            'geojson': geojson,
            'feature_count': len(geojson.get('features', []))
        })

    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

# ===================================
# Export Endpoints
# ===================================

@app.route('/api/export/geojson', methods=['POST'])
def export_geojson():
    """Export layer as GeoJSON"""
    try:
        data = request.json
        geojson = data.get('geojson')
        layer_name = data.get('layer_name', 'export')

        if not geojson:
            return jsonify({'error': 'No GeoJSON data provided'}), 400

        # Create JSON string
        json_str = json.dumps(geojson, indent=2)

        # Create in-memory file
        output = io.BytesIO()
        output.write(json_str.encode('utf-8'))
        output.seek(0)

        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'{layer_name}.geojson'
        )

    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/api/export/csv', methods=['POST'])
def export_csv():
    """Export point features as CSV"""
    try:
        data = request.json
        geojson = data.get('geojson')
        layer_name = data.get('layer_name', 'export')

        if not geojson:
            return jsonify({'error': 'No GeoJSON data provided'}), 400

        features = geojson.get('features', [])
        if not features:
            return jsonify({'error': 'No features to export'}), 400

        # Extract point features only
        point_features = [f for f in features if f['geometry']['type'] == 'Point']

        if not point_features:
            return jsonify({'error': 'No point features found. CSV export only supports points.'}), 400

        # Get all property keys
        all_keys = set()
        for feature in point_features:
            all_keys.update(feature.get('properties', {}).keys())

        # Create CSV
        output = io.StringIO()
        fieldnames = ['longitude', 'latitude'] + sorted(list(all_keys))
        writer = csv.DictWriter(output, fieldnames=fieldnames)

        writer.writeheader()
        for feature in point_features:
            coords = feature['geometry']['coordinates']
            row = {
                'longitude': coords[0],
                'latitude': coords[1]
            }
            row.update(feature.get('properties', {}))
            writer.writerow(row)

        # Convert to bytes
        csv_bytes = output.getvalue().encode('utf-8')
        bytes_output = io.BytesIO(csv_bytes)
        bytes_output.seek(0)

        return send_file(
            bytes_output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{layer_name}.csv'
        )

    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/api/export/kml', methods=['POST'])
def export_kml():
    """Export layer as KML"""
    try:
        data = request.json
        geojson = data.get('geojson')
        layer_name = data.get('layer_name', 'export')

        if not geojson:
            return jsonify({'error': 'No GeoJSON data provided'}), 400

        features = geojson.get('features', [])
        if not features:
            return jsonify({'error': 'No features to export'}), 400

        # Build KML
        kml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<kml xmlns="http://www.opengis.net/kml/2.2">',
            '<Document>',
            f'<name>{layer_name}</name>'
        ]

        for feature in features:
            geom = feature.get('geometry', {})
            props = feature.get('properties', {})

            name = props.get('name', 'Unnamed Feature')
            description_parts = [f'{k}: {v}' for k, v in props.items() if k != 'name']
            description = '<br/>'.join(description_parts) if description_parts else ''

            kml_parts.append('<Placemark>')
            kml_parts.append(f'<name>{name}</name>')
            if description:
                kml_parts.append(f'<description>{description}</description>')

            # Handle different geometry types
            if geom['type'] == 'Point':
                coords = geom['coordinates']
                kml_parts.append('<Point>')
                kml_parts.append(f'<coordinates>{coords[0]},{coords[1]},0</coordinates>')
                kml_parts.append('</Point>')

            elif geom['type'] == 'LineString':
                coords_str = ' '.join([f'{c[0]},{c[1]},0' for c in geom['coordinates']])
                kml_parts.append('<LineString>')
                kml_parts.append(f'<coordinates>{coords_str}</coordinates>')
                kml_parts.append('</LineString>')

            elif geom['type'] == 'Polygon':
                coords_str = ' '.join([f'{c[0]},{c[1]},0' for c in geom['coordinates'][0]])
                kml_parts.append('<Polygon>')
                kml_parts.append('<outerBoundaryIs><LinearRing>')
                kml_parts.append(f'<coordinates>{coords_str}</coordinates>')
                kml_parts.append('</LinearRing></outerBoundaryIs>')
                kml_parts.append('</Polygon>')

            kml_parts.append('</Placemark>')

        kml_parts.append('</Document>')
        kml_parts.append('</kml>')

        kml_content = '\n'.join(kml_parts)

        # Create in-memory file
        output = io.BytesIO()
        output.write(kml_content.encode('utf-8'))
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.google-earth.kml+xml',
            as_attachment=True,
            download_name=f'{layer_name}.kml'
        )

    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print(f"🗺️  Interactive Leaflet Map Viewer")
    print(f"{'='*60}")
    print(f"\nStarting server at: http://localhost:5000")
    print(f"Data directory: {DATA_DIR}")
    print(f"\nPress CTRL+C to quit\n")
    print(f"{'='*60}\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
