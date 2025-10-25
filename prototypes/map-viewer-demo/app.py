"""
Flask Backend for Interactive Leaflet Map Demo
Provides API endpoints for map data layers and preset configurations
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from pathlib import Path

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
CORS(app)

# Configuration
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
CONFIG_FILE = BASE_DIR / 'config.json'
PRESETS_FILE = BASE_DIR / 'data' / 'presets.json'

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
            "showScale": false
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
