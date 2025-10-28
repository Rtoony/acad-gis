# Interactive Leaflet Map Viewer - Prototype

A professional web-based demonstration application that showcases interactive mapping capabilities for engineering project presentations. Built with Leaflet.js and Flask, this tool provides dynamic presentation controls for toggling between different visualization modes, styling options, and data display methods in real-time.

## 🎯 Project Overview

This prototype demonstrates a full-featured map viewer with:
- Multiple basemap options (OpenStreetMap, Satellite, Terrain, etc.)
- Interactive data layers (Projects, Service Areas, Active Sites, Infrastructure)
- Real-time styling controls
- Professional presentation presets
- Export and sharing capabilities
- Responsive design for desktop and tablet presentations

## 📋 Table of Contents

- [Features](#features)
- [Technical Stack](#technical-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Customization](#customization)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Future Integration](#future-integration)

## ✨ Features

### Core Functionality

#### 1. **Basemap Management**
- 6 different basemap styles:
  - OpenStreetMap (default)
  - Grayscale (minimal design)
  - Satellite imagery
  - Terrain/topographic
  - Light (minimal labels)
  - Dark mode
- Adjustable basemap opacity (0-100%)
- Toggle to completely hide basemap

#### 2. **Data Visualization Layers**
- **Projects Layer**: 15 completed engineering projects with detailed information
- **Service Areas Layer**: Service coverage polygons showing geographic reach
- **Active Sites Layer**: 6 current projects with real-time status
- **Infrastructure Layer**: Network routes and utility corridors

#### 3. **Styling Controls**
- **Color Schemes**:
  - Company Brand colors
  - Standard colors
  - High Contrast (for accessibility)
  - Vibrant colors
  - Colorblind-friendly palette
- **Marker Sizing**: Small, Medium, Large
- **Font Sizing**: Small, Medium, Large
- **Label Toggle**: Show/hide labels on markers
- **Marker Clustering**: Group nearby markers for better visualization
- **Opacity Controls**: Separate controls for basemap and data layers

#### 4. **Preset Presentation Modes**
Five professionally designed presets for different scenarios:

1. **Executive Overview**
   - Satellite basemap
   - Major projects only
   - Large icons with company colors
   - Clean, high-level view

2. **Detailed Technical**
   - Topographic basemap
   - All data layers visible
   - Medium sizing
   - Scale bar and detailed popups

3. **Client Presentation**
   - Professional grayscale basemap
   - Selected projects highlighted
   - Branded colors
   - Optimized for presentations

4. **Print Ready**
   - High contrast design
   - Clear labels
   - Optimized for printing
   - No satellite imagery (ink-saving)

5. **Minimal Modern**
   - Very minimal basemap
   - Data-focused visualization
   - Bold colors
   - Clean, modern aesthetic

#### 5. **Interactive Tools**
- **Measurement Tool**: Measure distances on the map
- **Search Function**: Find locations (placeholder for geocoding)
- **Export Map**: Save current view as PNG image
- **Share Link**: Copy shareable URL to clipboard
- **Reset View**: Return to default map center and zoom
- **Print Mode**: Optimized print layout
- **Fullscreen Mode**: Maximize map view

#### 6. **Information Display**
- **Dynamic Legend**: Auto-updates based on active layers
- **Scale Bar**: Metric and imperial units
- **Popups**: Click or hover to see feature details
- **Tooltips**: Customizable tooltip behavior
- **Attribution**: Map data source credits

## 🛠 Technical Stack

### Frontend
- **HTML5**: Semantic structure
- **CSS3**: Modern styling with CSS variables
- **JavaScript (ES6)**: Core application logic
- **Leaflet.js 1.9.4**: Interactive mapping library
- **Leaflet Plugins**:
  - Leaflet.draw: Measurement tools
  - Leaflet.markercluster: Marker clustering
  - Leaflet.fullscreen: Fullscreen control
- **html2canvas**: Map export functionality
- **Font Awesome 6.4**: Icon library

### Backend
- **Python 3.8+**: Backend runtime
- **Flask 3.0**: Web framework
- **Flask-CORS**: Cross-origin resource sharing

### Data Formats
- **GeoJSON**: Spatial data format
- **JSON**: Configuration and presets

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Step-by-Step Setup

1. **Navigate to the prototype directory**
   ```bash
   cd prototypes/map-viewer-demo
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify directory structure**
   ```
   map-viewer-demo/
   ├── app.py                 # Flask application
   ├── config.json            # Configuration file
   ├── requirements.txt       # Python dependencies
   ├── data/                  # GeoJSON data files
   │   ├── projects.geojson
   │   ├── service_areas.geojson
   │   ├── active_sites.geojson
   │   └── infrastructure.geojson
   ├── templates/             # HTML templates
   │   └── index.html
   └── static/                # Static assets
       ├── css/
       │   └── styles.css
       └── js/
           └── app.js
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

   The application will be accessible at this URL. You should see the interactive map viewer with all controls loaded.

## 🚀 Usage

### Basic Navigation

1. **Pan**: Click and drag the map
2. **Zoom**: Use mouse wheel, +/- buttons, or double-click
3. **Fullscreen**: Click the fullscreen button in the top-right
4. **Reset View**: Click the "Reset" tool button

### Working with Layers

1. **Toggle Data Layers**:
   - Open the "Data Layers" section in the control panel
   - Check/uncheck layers to show/hide them
   - Adjust layer opacity with the slider

2. **View Feature Information**:
   - Click on markers, lines, or polygons to see detailed popups
   - Change tooltip mode in "Display Options" for hover behavior

### Changing Map Style

1. **Switch Basemaps**:
   - Open the "Basemap" section
   - Click any basemap option to switch
   - Adjust opacity or hide basemap entirely

2. **Apply Color Schemes**:
   - Open the "Styling" section
   - Select from 5 different color schemes
   - Changes apply immediately to all visible layers

3. **Adjust Marker Size**:
   - Use the marker size dropdown (Small/Medium/Large)
   - Useful for different presentation contexts

### Using Presets

1. **Quick Apply**:
   - Open the "Preset Modes" section
   - Click any preset card to instantly apply its settings
   - All map settings update automatically

2. **Save Custom Preset**:
   - Configure your desired map settings
   - Click "Save Current as Preset"
   - Enter name and description
   - Your preset is saved to the server

### Tools and Export

1. **Measure Distances**:
   - Click the "Measure" button
   - Use the drawing tools that appear
   - Click points on the map to measure

2. **Export Map**:
   - Click the "Export" button
   - Choose PNG format
   - Map image downloads automatically

3. **Share Current View**:
   - Click the "Share" button
   - Link is copied to clipboard
   - Share with colleagues or clients

## 🎨 Customization

### Modifying Company Information

Edit `config.json`:
```json
{
  "company_name": "Your Company Name",
  "map_center": [latitude, longitude],
  "initial_zoom": 10
}
```

### Adding New Data Layers

1. **Create GeoJSON file**:
   - Place in the `data/` directory
   - Name it descriptively (e.g., `my_layer.geojson`)

2. **GeoJSON structure**:
   ```json
   {
     "type": "FeatureCollection",
     "features": [
       {
         "type": "Feature",
         "properties": {
           "name": "Feature Name",
           "type": "category",
           "description": "Details..."
         },
         "geometry": {
           "type": "Point",
           "coordinates": [longitude, latitude]
         }
       }
     ]
   }
   ```

3. **Restart the server**: The new layer will appear automatically in the layers list

### Customizing Colors

Edit the color schemes in `config.json`:
```json
{
  "color_schemes": {
    "brand": {
      "primary": "#YOUR_COLOR",
      "secondary": "#YOUR_COLOR",
      "infrastructure": "#YOUR_COLOR",
      ...
    }
  }
}
```

### Adding New Basemaps

Edit `static/js/app.js` in the `setBasemap()` function:
```javascript
const basemaps = {
  your_basemap_id: {
    name: 'Your Basemap Name',
    url: 'https://tile-server-url/{z}/{x}/{y}.png',
    attribution: 'Your attribution',
    icon: 'fa-icon-name'
  },
  // ... other basemaps
};
```

### Modifying Presets

Edit the `get_default_presets()` function in `app.py` or save new presets through the UI.

## 📡 API Documentation

### GET `/`
Returns the main application HTML page.

### GET `/api/config`
Returns application configuration.

**Response:**
```json
{
  "company_name": "Engineering Solutions Inc.",
  "map_center": [37.7749, -122.4194],
  "initial_zoom": 10,
  "default_basemap": "osm"
}
```

### GET `/api/layers`
Returns list of available data layers.

**Response:**
```json
[
  {
    "name": "projects",
    "display_name": "Projects",
    "type": "geojson",
    "url": "/api/layer/projects"
  }
]
```

### GET `/api/layer/<layer_name>`
Returns GeoJSON data for a specific layer.

**Parameters:**
- `layer_name`: Name of the layer (e.g., "projects")

**Response:** GeoJSON FeatureCollection

### GET `/api/presets`
Returns all available preset configurations.

**Response:**
```json
{
  "executive_overview": {
    "name": "Executive Overview",
    "description": "Clean satellite basemap...",
    "basemap": "satellite",
    "layers": ["projects"],
    ...
  }
}
```

### GET `/api/preset/<preset_name>`
Returns a specific preset configuration.

### POST `/api/preset`
Saves a custom preset configuration.

**Request Body:**
```json
{
  "name": "My Custom Preset",
  "description": "Description here",
  "basemap": "osm",
  "layers": ["projects", "service_areas"],
  "markerSize": "large",
  ...
}
```

## 📁 Project Structure

```
map-viewer-demo/
│
├── app.py                      # Flask backend application
├── config.json                 # Application configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── data/                       # Data directory
│   ├── projects.geojson        # Engineering projects data
│   ├── service_areas.geojson   # Service coverage polygons
│   ├── active_sites.geojson    # Current active projects
│   ├── infrastructure.geojson  # Infrastructure networks
│   └── presets.json            # Saved user presets (auto-generated)
│
├── templates/                  # HTML templates
│   └── index.html              # Main application page
│
└── static/                     # Static assets
    ├── css/
    │   └── styles.css          # Application styles
    └── js/
        └── app.js              # Application JavaScript
```

## 🔮 Future Integration

This prototype is designed to be integrated into your main GIS application. Key integration points:

### 1. **DXF Overlay Integration**
The architecture supports adding DXF file visualization:
- Add DXF parsing library (e.g., `dxfgrabber` for Python)
- Create API endpoint to convert DXF to GeoJSON
- Add as a new data layer type
- Implement layer management in the UI

### 2. **Database Integration**
Replace GeoJSON files with database queries:
- Add database connector (PostgreSQL/PostGIS recommended)
- Modify `/api/layer/<layer_name>` to query database
- Implement spatial queries for performance
- Add real-time data updates

### 3. **Authentication & Authorization**
Add user management:
- Implement user login system
- Add role-based access control
- Restrict certain layers or presets by user role
- Add user-specific saved configurations

### 4. **Advanced GIS Capabilities**
Extend functionality:
- Spatial analysis tools (buffer, intersection, etc.)
- Advanced querying and filtering
- Data editing capabilities
- GPS tracking integration
- Real-time data streaming

### 5. **Backend Migration**
If needed, migrate to more robust backend:
- FastAPI for async capabilities
- Node.js for full JavaScript stack
- Django for comprehensive features
- GeoServer for advanced GIS backend

### 6. **Mobile Optimization**
Enhance mobile experience:
- Progressive Web App (PWA) capabilities
- Touch-optimized controls
- Offline data caching
- Mobile-specific presets

## 🧪 Testing

### Manual Testing Checklist

- [ ] Map loads correctly at startup
- [ ] All 6 basemaps switch properly
- [ ] All 4 data layers toggle on/off
- [ ] Opacity sliders work for basemap and layers
- [ ] All 5 color schemes apply correctly
- [ ] Marker sizes change appropriately
- [ ] Labels toggle on/off
- [ ] Marker clustering works
- [ ] All 5 presets apply correctly
- [ ] Custom preset can be saved
- [ ] Legend updates with active layers
- [ ] Scale bar toggles correctly
- [ ] Popups display feature information
- [ ] Measurement tool activates
- [ ] Export PNG works
- [ ] Share link copies to clipboard
- [ ] Reset view returns to default
- [ ] Fullscreen mode works
- [ ] Control panel collapses/expands
- [ ] Responsive design works on tablet

## 🐛 Troubleshooting

### Map doesn't load
- Check browser console for errors
- Verify Flask server is running
- Check network tab for failed requests
- Ensure all dependencies are installed

### Layers don't display
- Verify GeoJSON files exist in `data/` directory
- Check GeoJSON syntax is valid
- Look for JavaScript errors in console
- Verify file permissions

### Performance issues
- Reduce number of visible layers
- Enable marker clustering
- Simplify GeoJSON geometries
- Optimize basemap tile requests

### Export doesn't work
- Verify html2canvas is loaded
- Check browser compatibility
- Try different browsers
- Look for CORS issues

## 📝 License

This prototype is developed for internal use and demonstration purposes.

## 🤝 Support

For questions or issues with this prototype:
1. Check the troubleshooting section
2. Review browser console for errors
3. Verify all setup steps were completed
4. Contact your development team

## 🎯 Next Steps

To move from prototype to production:

1. **Data Integration**: Connect to your actual data sources
2. **DXF Support**: Implement DXF file parsing and visualization
3. **User Management**: Add authentication and authorization
4. **Performance**: Optimize for large datasets
5. **Testing**: Implement automated testing
6. **Deployment**: Set up production hosting
7. **Documentation**: Expand technical documentation
8. **Training**: Create user training materials

---

**Built with ❤️ using Leaflet.js and Flask**

**Version**: 1.0.0 (Prototype)
**Last Updated**: 2024
