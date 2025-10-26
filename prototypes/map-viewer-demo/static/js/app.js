/**
 * Interactive Map Viewer Application
 * Main JavaScript file for map functionality and UI controls
 */

// ===================================
// Performance Utilities
// ===================================

// Debounce function to limit expensive operations
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for high-frequency events
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Simple geometry simplification (reduce coordinate precision)
function simplifyGeometry(geometry, tolerance = 0.0001) {
    if (!geometry || !geometry.coordinates) return geometry;

    const simplifyCoord = (coord) => {
        if (Array.isArray(coord[0])) {
            return coord.map(simplifyCoord);
        }
        return coord.map(c => Math.round(c / tolerance) * tolerance);
    };

    return {
        ...geometry,
        coordinates: simplifyCoord(geometry.coordinates)
    };
}

// ===================================
// Global Variables and State
// ===================================

let map = null;
let currentBasemap = null;
let currentOverlay = null;
let config = {};
let presets = {};
let dataLayers = {};
let layerGroups = {};
let markerClusterGroup = null;
let measureControl = null;
let measurementLayer = null;
let currentMeasurementMode = 'distance';
let measurementHandlersInitialized = false;
let searchMarker = null;
let searchHandlersInitialized = false;
let currentColorScheme = 'standard';
let currentState = {
    basemap: 'osm',
    layers: [],
    markerSize: 'medium',
    fontSize: 'medium',
    showLabels: true,
    clusterMarkers: false,
    basemapOpacity: 100,
    layerOpacity: 85,
    colorScheme: 'standard',
    showLegend: true,
    showScale: true,
    showAttribution: true,
    tooltipMode: 'click'
};

// ===================================
// Initialization
// ===================================

document.addEventListener('DOMContentLoaded', async () => {
    try {
        showLoading(true);
        await loadConfig();
        initializeMap();
        await loadLayers();
        await loadPresets();
        initializeUI();
        initializeControls();
        setupEventListeners();
        showLoading(false);
    } catch (error) {
        console.error('Initialization error:', error);
        showLoading(false);
        alert('Error loading map viewer. Please refresh the page.');
    }
});

// ===================================
// Configuration and Data Loading
// ===================================

// ===================================
// Error Notification System
// ===================================

function showError(message, duration = 5000) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
        <button class="error-close">&times;</button>
    `;

    document.body.appendChild(errorDiv);

    const closeBtn = errorDiv.querySelector('.error-close');
    closeBtn.addEventListener('click', () => {
        errorDiv.classList.add('fade-out');
        setTimeout(() => errorDiv.remove(), 300);
    });

    setTimeout(() => {
        errorDiv.classList.add('fade-out');
        setTimeout(() => errorDiv.remove(), 300);
    }, duration);
}

function showSuccess(message, duration = 3000) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-notification';
    successDiv.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(successDiv);

    setTimeout(() => {
        successDiv.classList.add('fade-out');
        setTimeout(() => successDiv.remove(), 300);
    }, duration);
}

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        config = await response.json();
    } catch (error) {
        console.error('Error loading config:', error);
        showError('Failed to load configuration. Using default settings.');
        // Use defaults if config fails to load
        config = {
            map_center: [38.5, -122.8],
            initial_zoom: 10,
            default_basemap: 'osm'
        };
    }
}

async function loadLayers() {
    showLoading(true);
    try {
        const response = await fetch('/api/layers');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const layers = await response.json();

        for (const layer of layers) {
            try {
                const dataResponse = await fetch(layer.url);
                if (!dataResponse.ok) {
                    throw new Error(`HTTP error! status: ${dataResponse.status}`);
                }
                let data = await dataResponse.json();

                // Optimize complex geometries for better performance
                if (data.features && data.features.length > 0) {
                    data.features = data.features.map(feature => {
                        // Simplify complex geometries (polygons and lines)
                        if (feature.geometry &&
                            (feature.geometry.type === 'Polygon' ||
                             feature.geometry.type === 'MultiPolygon' ||
                             feature.geometry.type === 'LineString' ||
                             feature.geometry.type === 'MultiLineString')) {

                            // Count coordinates to determine if simplification is needed
                            const coordCount = JSON.stringify(feature.geometry.coordinates).length;
                            if (coordCount > 1000) {
                                // Simplify complex geometries
                                feature.geometry = simplifyGeometry(feature.geometry, 0.001);
                            }
                        }
                        return feature;
                    });
                }

                dataLayers[layer.name] = {
                    ...layer,
                    data: data,
                    visible: false,
                    featureCount: data.features ? data.features.length : 0
                };

                console.log(`Loaded layer ${layer.name}: ${dataLayers[layer.name].featureCount} features`);
            } catch (layerError) {
                console.error(`Error loading layer ${layer.name}:`, layerError);
                showError(`Failed to load layer: ${layer.display_name || layer.name}`);
            }
        }

        populateLayersList();
        showLoading(false);
    } catch (error) {
        console.error('Error loading layers:', error);
        showError('Failed to load data layers. Please refresh the page.');
        showLoading(false);
    }
}

async function loadPresets() {
    try {
        const response = await fetch('/api/presets');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        presets = await response.json();
        populatePresetsList();
    } catch (error) {
        console.error('Error loading presets:', error);
        showError('Failed to load preset modes. Preset functionality may be limited.');
    }
}

// ===================================
// Map Initialization
// ===================================

function initializeMap() {
    // Create map with enhanced zoom settings
    map = L.map('map', {
        center: config.map_center || [38.5, -122.8],
        zoom: config.initial_zoom || 10,
        minZoom: 3,
        maxZoom: 20,  // Allow deeper zoom (default is 18)
        zoomDelta: 0.5,  // Smaller increments (default is 1)
        zoomSnap: 0.5,  // Snap to half-zoom levels
        wheelPxPerZoomLevel: 120,  // Finer scroll control
        zoomControl: true,
        fullscreenControl: true,
        fullscreenControlOptions: {
            position: 'topleft'
        }
    });

    // Set initial basemap
    setBasemap(config.default_basemap || 'osm');

    // Initialize marker cluster group with optimized settings
    markerClusterGroup = L.markerClusterGroup({
        maxClusterRadius: 50,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: true,
        zoomToBoundsOnClick: true,
        disableClusteringAtZoom: 18, // Disable clustering at high zoom for better performance
        chunkedLoading: true, // Load markers in chunks for better performance
        chunkInterval: 200, // Milliseconds between processing chunks
        chunkDelay: 50, // Milliseconds to delay before starting chunk processing
        animate: true,
        animateAddingMarkers: false, // Disable animation when adding many markers for performance
        removeOutsideVisibleBounds: true // Remove markers outside visible bounds for memory optimization
    });

    // Add scale control
    L.control.scale({
        position: 'bottomleft',
        imperial: true,
        metric: true
    }).addTo(map);

    // Initialize measurement control
    measureControl = new L.Control.Draw({
        draw: {
            polyline: {
                shapeOptions: {
                    color: '#f357a1',
                    weight: 4
                },
                metric: true,
                feet: false
            },
            polygon: false,
            circle: false,
            rectangle: false,
            marker: false,
            circlemarker: false
        },
        edit: false
    });

    // Initialize coordinate display
    initCoordinateDisplay();
}

// ===================================
// Coordinate Display
// ===================================

function initCoordinateDisplay() {
    const coordDisplay = document.getElementById('coordinateDisplay');
    const coordsText = document.getElementById('coordsText');

    // Throttled coordinate update for performance
    const updateCoordinates = throttle((e) => {
        const lat = e.latlng.lat.toFixed(6);
        const lng = e.latlng.lng.toFixed(6);
        coordsText.textContent = `Lat: ${lat}, Lon: ${lng}`;
    }, 50); // Update every 50ms max

    // Track mouse movement on map
    map.on('mousemove', updateCoordinates);

    // Hide when mouse leaves map
    map.on('mouseout', () => {
        coordsText.textContent = 'Hover over map to see coordinates';
    });
}

// ===================================
// Keyboard Shortcuts
// ===================================

function initKeyboardShortcuts() {
    let lastMousePosition = null;

    // Track mouse position for copy coordinates shortcut
    map.on('mousemove', (e) => {
        lastMousePosition = e.latlng;
    });

    document.addEventListener('keydown', (e) => {
        // Don't trigger shortcuts if user is typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        switch(e.key.toLowerCase()) {
            case 'f':
                // Toggle fullscreen
                if (document.fullscreenElement) {
                    document.exitFullscreen();
                } else {
                    document.documentElement.requestFullscreen();
                }
                break;

            case 'l':
                // Toggle legend
                const legend = document.getElementById('legend');
                legend.classList.toggle('hidden');
                break;

            case 'escape':
                // Close any open modals
                document.querySelectorAll('.modal').forEach(modal => {
                    modal.style.display = 'none';
                });
                break;

            case 'r':
                // Reset view
                if (config.map_center) {
                    map.setView(config.map_center, config.initial_zoom || 10);
                    showSuccess('View reset to default');
                }
                break;

            case 'c':
                // Copy coordinates at mouse position
                if (lastMousePosition) {
                    const lat = lastMousePosition.lat.toFixed(6);
                    const lng = lastMousePosition.lng.toFixed(6);
                    const coordString = `${lat}, ${lng}`;

                    navigator.clipboard.writeText(coordString).then(() => {
                        showSuccess(`Coordinates copied: ${coordString}`);
                    }).catch(() => {
                        showError('Failed to copy coordinates to clipboard');
                    });
                }
                break;

            case '+':
            case '=':
                // Zoom in
                map.zoomIn();
                break;

            case '-':
                // Zoom out
                map.zoomOut();
                break;

            case '?':
            case 'h':
                // Show keyboard shortcuts help
                showKeyboardShortcutsHelp();
                break;
        }
    });
}

function showKeyboardShortcutsHelp() {
    const helpText = `
        <div style="text-align: left; line-height: 1.8;">
            <h3 style="margin-top: 0;">⌨️ Keyboard Shortcuts</h3>
            <p><strong>F</strong> - Toggle Fullscreen</p>
            <p><strong>L</strong> - Toggle Legend</p>
            <p><strong>R</strong> - Reset View</p>
            <p><strong>C</strong> - Copy Coordinates (at mouse position)</p>
            <p><strong>+/=</strong> - Zoom In</p>
            <p><strong>-</strong> - Zoom Out</p>
            <p><strong>Esc</strong> - Close Modals</p>
            <p><strong>? or H</strong> - Show This Help</p>
        </div>
    `;

    // Create temporary modal for shortcuts
    const helpModal = document.createElement('div');
    helpModal.className = 'modal';
    helpModal.style.display = 'flex';
    helpModal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3>Keyboard Shortcuts</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                ${helpText}
            </div>
        </div>
    `;

    document.body.appendChild(helpModal);

    // Close handlers
    const closeBtn = helpModal.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => {
        helpModal.remove();
    });

    helpModal.addEventListener('click', (e) => {
        if (e.target === helpModal) {
            helpModal.remove();
        }
    });
}

// ===================================
// Basemap Management
// ===================================

function setBasemap(basemapId) {
    const basemaps = {
        osm: {
            name: 'OpenStreetMap',
            url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attribution: '&copy; OpenStreetMap contributors',
            icon: 'fa-map'
        },
        grayscale: {
            name: 'Grayscale',
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
            attribution: 'Esri, HERE, Garmin',
            icon: 'fa-adjust'
        },
        satellite: {
            name: 'Satellite',
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attribution: 'Esri, Maxar, GeoEye',
            icon: 'fa-satellite'
        },
        terrain: {
            name: 'Terrain',
            url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            attribution: '&copy; OpenTopoMap contributors',
            icon: 'fa-mountain'
        },
        light: {
            name: 'Light',
            url: 'https://{s}.basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}{r}.png',
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            icon: 'fa-sun'
        },
        dark: {
            name: 'Dark',
            url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            icon: 'fa-moon'
        },
        streets: {
            name: 'Streets',
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
            attribution: 'Esri, DeLorme, NAVTEQ',
            icon: 'fa-road'
        },
        watercolor: {
            name: 'Watercolor (Artistic)',
            url: 'https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg',
            attribution: 'Map tiles by Stamen Design, under CC BY 3.0. Hosted by Stadia Maps',
            icon: 'fa-palette'
        },
        voyager: {
            name: 'Voyager (Balanced)',
            url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            icon: 'fa-compass'
        },
        topo: {
            name: 'Topographic (USGS)',
            url: 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}',
            attribution: 'USGS',
            icon: 'fa-layer-group'
        },
        hot: {
            name: 'Humanitarian (HOT)',
            url: 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
            attribution: '&copy; OpenStreetMap contributors, Tiles style by Humanitarian OpenStreetMap Team',
            icon: 'fa-heart'
        },
        hybrid: {
            name: 'Satellite + Labels',
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attribution: 'Esri, Maxar, GeoEye',
            icon: 'fa-globe',
            overlay: 'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'
        },
        darkmatter: {
            name: 'Midnight (Dark Gray)',
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
            attribution: 'Esri, HERE, Garmin',
            icon: 'fa-moon'
        },
        natgeo: {
            name: 'National Geographic',
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
            attribution: 'Esri, National Geographic',
            icon: 'fa-globe-americas'
        },
        positron: {
            name: 'Alidade Smooth',
            url: 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png',
            attribution: '&copy; Stadia Maps &copy; OpenMapTiles &copy; OpenStreetMap',
            icon: 'fa-circle-notch'
        },
        ocean: {
            name: 'Ocean Basemap',
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
            attribution: 'Esri, GEBCO, NOAA, NGS',
            icon: 'fa-water'
        }
    };

    try {
        // Remove current basemap and overlay
        if (currentBasemap) {
            map.removeLayer(currentBasemap);
        }
        if (currentOverlay) {
            map.removeLayer(currentOverlay);
            currentOverlay = null;
        }

        // Add new basemap
        const basemap = basemaps[basemapId];
        if (!basemap) {
            throw new Error(`Basemap ${basemapId} not found`);
        }

        currentBasemap = L.tileLayer(basemap.url, {
            attribution: basemap.attribution,
            opacity: currentState.basemapOpacity / 100
        }).addTo(map);

        // Listen for tile load errors
        currentBasemap.on('tileerror', function(error) {
            console.warn('Basemap tile load error:', error);
        });

        // Add overlay if specified (for hybrid maps)
        if (basemap.overlay) {
            currentOverlay = L.tileLayer(basemap.overlay, {
                attribution: '',
                opacity: 0.8
            }).addTo(map);

            currentOverlay.on('tileerror', function(error) {
                console.warn('Overlay tile load error:', error);
            });
        }

        currentState.basemap = basemapId;

        // Update UI
        document.querySelectorAll('.basemap-option').forEach(option => {
            option.classList.remove('active');
        });
        const activeOption = document.querySelector(`[data-basemap="${basemapId}"]`);
        if (activeOption) {
            activeOption.classList.add('active');
        }

        showSuccess(`Basemap changed to ${basemap.name}`);
    } catch (error) {
        console.error('Error changing basemap:', error);
        showError(`Failed to load basemap. ${error.message}`);
    }
}

function populateBasemapGrid() {
    const basemaps = [
        { id: 'osm', name: 'OpenStreetMap', icon: 'fa-map' },
        { id: 'grayscale', name: 'Grayscale', icon: 'fa-adjust' },
        { id: 'satellite', name: 'Satellite', icon: 'fa-satellite' },
        { id: 'terrain', name: 'Terrain', icon: 'fa-mountain' },
        { id: 'light', name: 'Light', icon: 'fa-sun' },
        { id: 'dark', name: 'Dark', icon: 'fa-moon' },
        { id: 'streets', name: 'Streets', icon: 'fa-road' },
        { id: 'watercolor', name: 'Watercolor (Artistic)', icon: 'fa-palette' },
        { id: 'voyager', name: 'Voyager (Balanced)', icon: 'fa-compass' },
        { id: 'topo', name: 'Topographic (USGS)', icon: 'fa-layer-group' },
        { id: 'hot', name: 'Humanitarian (HOT)', icon: 'fa-heart' },
        { id: 'hybrid', name: 'Satellite + Labels', icon: 'fa-globe' },
        { id: 'darkmatter', name: 'Midnight (Dark Gray)', icon: 'fa-moon' },
        { id: 'natgeo', name: 'National Geographic', icon: 'fa-globe-americas' },
        { id: 'positron', name: 'Alidade Smooth', icon: 'fa-circle-notch' },
        { id: 'ocean', name: 'Ocean Basemap', icon: 'fa-water' }
    ];

    const grid = document.getElementById('basemapGrid');
    grid.innerHTML = '';

    basemaps.forEach(basemap => {
        const option = document.createElement('div');
        option.className = 'basemap-option';
        option.dataset.basemap = basemap.id;
        if (basemap.id === currentState.basemap) {
            option.classList.add('active');
        }

        option.innerHTML = `
            <i class="fas ${basemap.icon}"></i>
            <span>${basemap.name}</span>
        `;

        option.addEventListener('click', () => setBasemap(basemap.id));
        grid.appendChild(option);
    });
}

// ===================================
// Data Layer Management
// ===================================

function toggleLayer(layerName, visible) {
    if (!dataLayers[layerName]) return;

    dataLayers[layerName].visible = visible;

    if (visible) {
        addLayerToMap(layerName);
        if (!currentState.layers.includes(layerName)) {
            currentState.layers.push(layerName);
        }
    } else {
        removeLayerFromMap(layerName);
        currentState.layers = currentState.layers.filter(l => l !== layerName);
    }

    updateLegend();
}

function addLayerToMap(layerName) {
    try {
        const layer = dataLayers[layerName];
        if (!layer || !layer.data) {
            throw new Error(`Layer ${layerName} not found or has no data`);
        }

        // Remove existing layer group if it exists
        removeLayerFromMap(layerName);

        const layerGroup = L.geoJSON(layer.data, {
            pointToLayer: (feature, latlng) => createMarker(feature, latlng, layerName),
            style: (feature) => getFeatureStyle(feature, layerName),
            onEachFeature: (feature, layer) => bindFeaturePopup(feature, layer)
        });

    if (currentState.clusterMarkers && layerName === 'projects') {
        markerClusterGroup.clearLayers();
        layerGroup.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                markerClusterGroup.addLayer(layer);
            }
        });
        map.addLayer(markerClusterGroup);
    } else {
        layerGroup.addTo(map);
    }

        layerGroups[layerName] = layerGroup;

        // Apply opacity
        if (layerGroup.setOpacity) {
            layerGroup.setOpacity(currentState.layerOpacity / 100);
        }
    } catch (error) {
        console.error(`Error adding layer ${layerName} to map:`, error);
        showError(`Failed to display layer: ${dataLayers[layerName]?.display_name || layerName}`);
    }
}

function removeLayerFromMap(layerName) {
    if (layerGroups[layerName]) {
        map.removeLayer(layerGroups[layerName]);
        delete layerGroups[layerName];
    }

    if (layerName === 'projects' && currentState.clusterMarkers) {
        markerClusterGroup.clearLayers();
        map.removeLayer(markerClusterGroup);
    }
}

function createMarker(feature, latlng, layerName) {
    const projectType = feature.properties.type || 'default';
    const color = getColorForType(projectType);
    const size = getMarkerSize();

    let icon;

    if (layerName === 'active_sites') {
        // Different icon for active sites
        icon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: ${color}; width: ${size}px; height: ${size}px;
                   border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                   animation: pulse 2s infinite;"></div>`,
            iconSize: [size, size],
            iconAnchor: [size / 2, size / 2]
        });
    } else {
        icon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: ${color}; width: ${size}px; height: ${size}px;
                   border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>`,
            iconSize: [size, size],
            iconAnchor: [size / 2, size / 2]
        });
    }

    const marker = L.marker(latlng, { icon: icon });

    // Add permanent label if enabled
    if (currentState.showLabels && feature.properties.name) {
        marker.bindTooltip(feature.properties.name, {
            permanent: true,
            direction: 'top',
            className: 'marker-label',
            offset: [0, -size / 2 - 5]
        });
    }

    return marker;
}

function getFeatureStyle(feature, layerName) {
    const type = feature.properties.type || feature.properties.infrastructure_type || 'default';
    const color = getColorForType(type);

    if (feature.geometry.type === 'LineString' || feature.geometry.type === 'MultiLineString') {
        return {
            color: color,
            weight: 4,
            opacity: currentState.layerOpacity / 100,
            dashArray: type === 'utilities' ? '10, 5' : null
        };
    }

    if (feature.geometry.type === 'Polygon' || feature.geometry.type === 'MultiPolygon') {
        const opacity = layerName === 'service_areas' ? 0.3 : 0.5;
        return {
            fillColor: color,
            fillOpacity: opacity * (currentState.layerOpacity / 100),
            color: color,
            weight: 2,
            opacity: currentState.layerOpacity / 100
        };
    }

    return {};
}

function bindFeaturePopup(feature, layer) {
    if (!feature.properties) return;

    const props = feature.properties;
    let popupContent = `<div class="popup-header">${props.name || 'Feature'}</div>`;
    popupContent += '<div class="popup-body">';

    // Add relevant properties
    const excludeKeys = ['name'];
    Object.keys(props).forEach(key => {
        if (!excludeKeys.includes(key) && props[key]) {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            popupContent += `
                <div class="popup-row">
                    <span class="popup-label">${label}:</span>
                    <span class="popup-value">${props[key]}</span>
                </div>
            `;
        }
    });

    popupContent += '</div>';

    if (currentState.tooltipMode === 'click') {
        layer.bindPopup(popupContent);
    } else if (currentState.tooltipMode === 'hover') {
        layer.bindTooltip(popupContent, { sticky: true });
    }
}

function populateLayersList() {
    const layersList = document.getElementById('layersList');
    layersList.innerHTML = '';

    const layerIcons = {
        projects: 'fa-project-diagram',
        service_areas: 'fa-draw-polygon',
        active_sites: 'fa-hard-hat',
        infrastructure: 'fa-road'
    };

    Object.keys(dataLayers).forEach(layerName => {
        const layer = dataLayers[layerName];
        const featureCount = layer.data.features ? layer.data.features.length : 0;

        const item = document.createElement('div');
        item.className = 'layer-item';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `layer-${layerName}`;
        checkbox.checked = layer.visible;
        checkbox.addEventListener('change', (e) => {
            toggleLayer(layerName, e.target.checked);
        });

        const icon = document.createElement('div');
        icon.className = 'layer-icon';
        icon.innerHTML = `<i class="fas ${layerIcons[layerName] || 'fa-layer-group'}"></i>`;

        const info = document.createElement('div');
        info.className = 'layer-info';
        info.innerHTML = `
            <div class="layer-name">${layer.display_name}</div>
            <div class="layer-count">${featureCount} features</div>
        `;

        item.appendChild(checkbox);
        item.appendChild(icon);
        item.appendChild(info);

        item.addEventListener('click', (e) => {
            if (e.target !== checkbox) {
                checkbox.checked = !checkbox.checked;
                toggleLayer(layerName, checkbox.checked);
            }
        });

        layersList.appendChild(item);
    });
}

// ===================================
// Styling and Color Management
// ===================================

function getColorScheme() {
    const schemes = {
        brand: {
            primary: '#2C5AA0',
            secondary: '#4A90E2',
            accent: '#F5A623',
            infrastructure: '#2C5AA0',
            commercial: '#4A90E2',
            residential: '#7ED321',
            environmental: '#50C878',
            transportation: '#F5A623',
            utilities: '#D0021B'
        },
        standard: {
            primary: '#3388ff',
            secondary: '#38A9DC',
            accent: '#FFC107',
            infrastructure: '#3388ff',
            commercial: '#38A9DC',
            residential: '#4CAF50',
            environmental: '#8BC34A',
            transportation: '#FF9800',
            utilities: '#F44336'
        },
        high_contrast: {
            primary: '#000000',
            secondary: '#333333',
            accent: '#FF0000',
            infrastructure: '#000000',
            commercial: '#0000FF',
            residential: '#00AA00',
            environmental: '#008000',
            transportation: '#FF8800',
            utilities: '#CC0000'
        },
        vibrant: {
            primary: '#E91E63',
            secondary: '#9C27B0',
            accent: '#00BCD4',
            infrastructure: '#E91E63',
            commercial: '#9C27B0',
            residential: '#4CAF50',
            environmental: '#8BC34A',
            transportation: '#FF9800',
            utilities: '#F44336'
        },
        colorblind_friendly: {
            primary: '#0173B2',
            secondary: '#029E73',
            accent: '#ECE133',
            infrastructure: '#0173B2',
            commercial: '#029E73',
            residential: '#56B4E9',
            environmental: '#CC78BC',
            transportation: '#F0E442',
            utilities: '#DE8F05'
        }
    };

    return schemes[currentState.colorScheme] || schemes.standard;
}

function getColorForType(type) {
    const colorScheme = getColorScheme();
    return colorScheme[type] || colorScheme.primary;
}

function getMarkerSize() {
    const sizes = {
        small: 12,
        medium: 16,
        large: 24
    };
    return sizes[currentState.markerSize] || 16;
}

function applyColorScheme(scheme) {
    currentState.colorScheme = scheme;

    // Reload visible layers
    const visibleLayers = currentState.layers.slice();
    visibleLayers.forEach(layerName => {
        addLayerToMap(layerName);
    });

    updateLegend();
}

function applyMarkerSize(size) {
    currentState.markerSize = size;

    // Reload visible layers with point features
    const visibleLayers = currentState.layers.slice();
    visibleLayers.forEach(layerName => {
        addLayerToMap(layerName);
    });
}

function applyFontSize(size) {
    currentState.fontSize = size;

    // Update the dynamic styles
    updateMarkerStyles();

    // Reload visible layers to apply new font sizes to labels
    const visibleLayers = currentState.layers.slice();
    visibleLayers.forEach(layerName => {
        addLayerToMap(layerName);
    });

    // Update legend if visible
    updateLegend();
}

// ===================================
// Legend Management
// ===================================

function updateLegend() {
    const legendContent = document.getElementById('legendContent');
    legendContent.innerHTML = '';

    const colorScheme = getColorScheme();
    const types = new Set();

    // Collect all types from visible layers
    currentState.layers.forEach(layerName => {
        const layer = dataLayers[layerName];
        if (layer && layer.data && layer.data.features) {
            layer.data.features.forEach(feature => {
                const type = feature.properties.type || feature.properties.infrastructure_type;
                if (type) types.add(type);
            });
        }
    });

    // Create legend items
    types.forEach(type => {
        const item = document.createElement('div');
        item.className = 'legend-item';

        const color = getColorForType(type);
        const label = type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        item.innerHTML = `
            <div class="legend-color" style="background-color: ${color}"></div>
            <span>${label}</span>
        `;

        legendContent.appendChild(item);
    });

    // Show/hide legend based on setting
    const legend = document.getElementById('legend');
    legend.classList.toggle('hidden', !currentState.showLegend || types.size === 0);
}

// ===================================
// Preset Management
// ===================================

function populatePresetsList() {
    const presetsList = document.getElementById('presetsList');
    presetsList.innerHTML = '';

    const presetOrder = [
        'executive_overview',
        'detailed_technical',
        'client_presentation',
        'print_ready',
        'minimal_modern'
    ];

    presetOrder.forEach(presetId => {
        if (presets[presetId]) {
            const preset = presets[presetId];
            const card = document.createElement('div');
            card.className = 'preset-card';
            card.dataset.preset = presetId;

            card.innerHTML = `
                <div class="preset-name">${preset.name || presetId}</div>
                <div class="preset-description">${preset.description || ''}</div>
            `;

            card.addEventListener('click', () => applyPreset(presetId));
            presetsList.appendChild(card);
        }
    });
}

function applyPreset(presetId) {
    const preset = presets[presetId];
    if (!preset) return;

    // Apply basemap
    if (preset.basemap) {
        setBasemap(preset.basemap);
    }

    // Apply layers
    if (preset.layers) {
        // Turn off all layers
        Object.keys(dataLayers).forEach(layerName => {
            dataLayers[layerName].visible = false;
            const checkbox = document.getElementById(`layer-${layerName}`);
            if (checkbox) checkbox.checked = false;
        });

        // Turn on preset layers
        preset.layers.forEach(layerName => {
            if (dataLayers[layerName]) {
                dataLayers[layerName].visible = true;
                const checkbox = document.getElementById(`layer-${layerName}`);
                if (checkbox) checkbox.checked = true;
                addLayerToMap(layerName);
            }
        });

        currentState.layers = preset.layers.slice();
    }

    // Apply styling
    if (preset.markerSize) {
        currentState.markerSize = preset.markerSize;
        document.getElementById('markerSize').value = preset.markerSize;
    }

    if (preset.fontSize) {
        currentState.fontSize = preset.fontSize;
        document.getElementById('fontSize').value = preset.fontSize;
    }

    if (preset.colorScheme) {
        currentState.colorScheme = preset.colorScheme;
        document.getElementById('colorScheme').value = preset.colorScheme;
        applyColorScheme(preset.colorScheme);
    }

    if (preset.showLabels !== undefined) {
        currentState.showLabels = preset.showLabels;
        document.getElementById('showLabels').checked = preset.showLabels;
    }

    if (preset.basemapOpacity !== undefined) {
        currentState.basemapOpacity = preset.basemapOpacity;
        document.getElementById('basemapOpacity').value = preset.basemapOpacity;
        document.getElementById('basemapOpacityValue').textContent = `${preset.basemapOpacity}%`;
        if (currentBasemap) {
            currentBasemap.setOpacity(preset.basemapOpacity / 100);
        }
    }

    if (preset.layerOpacity !== undefined) {
        currentState.layerOpacity = preset.layerOpacity;
        document.getElementById('layerOpacity').value = preset.layerOpacity;
        document.getElementById('layerOpacityValue').textContent = `${preset.layerOpacity}%`;
    }

    if (preset.showLegend !== undefined) {
        currentState.showLegend = preset.showLegend;
        document.getElementById('showLegend').checked = preset.showLegend;
    }

    if (preset.showScale !== undefined) {
        currentState.showScale = preset.showScale;
        document.getElementById('showScale').checked = preset.showScale;
    }

    // Reload all visible layers
    const visibleLayers = currentState.layers.slice();
    visibleLayers.forEach(layerName => {
        addLayerToMap(layerName);
    });

    updateLegend();

    // Update UI
    document.querySelectorAll('.preset-card').forEach(card => {
        card.classList.remove('active');
    });
    const activeCard = document.querySelector(`[data-preset="${presetId}"]`);
    if (activeCard) {
        activeCard.classList.add('active');
    }
}

async function saveCustomPreset(name, description) {
    const preset = {
        name: name,
        description: description,
        ...currentState
    };

    try {
        const response = await fetch('/api/preset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(preset)
        });

        const result = await response.json();
        if (result.success) {
            alert('Preset saved successfully!');
            await loadPresets();
        } else {
            alert('Error saving preset: ' + result.error);
        }
    } catch (error) {
        console.error('Error saving preset:', error);
        alert('Error saving preset');
    }
}

// ===================================
// UI Initialization and Event Handlers
// ===================================

function initializeUI() {
    populateBasemapGrid();
    updateLegend();
}

function initializeControls() {
    // Basemap opacity
    const basemapOpacity = document.getElementById('basemapOpacity');
    basemapOpacity.addEventListener('input', (e) => {
        const value = e.target.value;
        currentState.basemapOpacity = parseInt(value);
        document.getElementById('basemapOpacityValue').textContent = `${value}%`;
        if (currentBasemap) {
            currentBasemap.setOpacity(value / 100);
        }
    });

    // Hide basemap
    document.getElementById('hideBasemap').addEventListener('change', (e) => {
        if (currentBasemap) {
            if (e.target.checked) {
                currentBasemap.setOpacity(0);
            } else {
                currentBasemap.setOpacity(currentState.basemapOpacity / 100);
            }
        }
    });

    // Layer opacity
    const layerOpacity = document.getElementById('layerOpacity');
    layerOpacity.addEventListener('input', (e) => {
        const value = e.target.value;
        currentState.layerOpacity = parseInt(value);
        document.getElementById('layerOpacityValue').textContent = `${value}%`;

        // Update all visible layers
        currentState.layers.forEach(layerName => {
            if (layerGroups[layerName]) {
                if (layerGroups[layerName].setOpacity) {
                    layerGroups[layerName].setOpacity(value / 100);
                } else {
                    layerGroups[layerName].setStyle({ opacity: value / 100, fillOpacity: (value / 100) * 0.5 });
                }
            }
        });
    });

    // Color scheme
    document.getElementById('colorScheme').addEventListener('change', (e) => {
        applyColorScheme(e.target.value);
    });

    // Marker size
    document.getElementById('markerSize').addEventListener('change', (e) => {
        applyMarkerSize(e.target.value);
    });

    // Font size
    document.getElementById('fontSize').addEventListener('change', (e) => {
        applyFontSize(e.target.value);
    });

    // Show labels
    document.getElementById('showLabels').addEventListener('change', (e) => {
        currentState.showLabels = e.target.checked;
        // Reload visible layers to apply label changes
        const visibleLayers = currentState.layers.slice();
        visibleLayers.forEach(layerName => {
            addLayerToMap(layerName);
        });
    });

    // Cluster markers
    document.getElementById('clusterMarkers').addEventListener('change', (e) => {
        currentState.clusterMarkers = e.target.checked;
        // Reload project layer if visible
        if (currentState.layers.includes('projects')) {
            addLayerToMap('projects');
        }
    });

    // Display options
    document.getElementById('showLegend').addEventListener('change', (e) => {
        currentState.showLegend = e.target.checked;
        updateLegend();
    });

    document.getElementById('showScale').addEventListener('change', (e) => {
        currentState.showScale = e.target.checked;
        const scaleControl = document.querySelector('.leaflet-control-scale');
        if (scaleControl) {
            scaleControl.style.display = e.target.checked ? 'block' : 'none';
        }
    });

    document.getElementById('showAttribution').addEventListener('change', (e) => {
        currentState.showAttribution = e.target.checked;
        const attribution = document.querySelector('.leaflet-control-attribution');
        if (attribution) {
            attribution.style.display = e.target.checked ? 'block' : 'none';
        }
    });

    document.getElementById('tooltipMode').addEventListener('change', (e) => {
        currentState.tooltipMode = e.target.value;
        // Reload visible layers to apply tooltip mode
        const visibleLayers = currentState.layers.slice();
        visibleLayers.forEach(layerName => {
            addLayerToMap(layerName);
        });
    });
}

function setupEventListeners() {
    // Panel toggle
    document.getElementById('togglePanel').addEventListener('click', () => {
        document.getElementById('controlPanel').classList.toggle('collapsed');
    });

    // Fullscreen
    document.getElementById('fullscreenBtn').addEventListener('click', () => {
        if (map.isFullscreen()) {
            map.toggleFullscreen();
        } else {
            map.toggleFullscreen();
        }
    });

    // Section toggles
    document.querySelectorAll('.section-header').forEach(header => {
        header.addEventListener('click', () => {
            header.classList.toggle('active');
            const content = header.nextElementSibling;
            content.classList.toggle('collapsed');
        });
    });

    // Tool buttons
    document.getElementById('measureBtn').addEventListener('click', () => {
        showMeasurementPanel();
    });

    document.getElementById('searchBtn').addEventListener('click', () => {
        showSearchPanel();
    });

    document.getElementById('exportBtn').addEventListener('click', () => {
        showExportModal();
    });

    document.getElementById('shareBtn').addEventListener('click', () => {
        const url = window.location.href;
        navigator.clipboard.writeText(url).then(() => {
            alert('Link copied to clipboard!');
        });
    });

    document.getElementById('resetBtn').addEventListener('click', () => {
        map.setView(config.map_center || [37.7749, -122.4194], config.initial_zoom || 10);
    });

    document.getElementById('printBtn').addEventListener('click', () => {
        window.print();
    });

    // Save preset button
    document.getElementById('savePresetBtn').addEventListener('click', () => {
        showSavePresetModal();
    });

    // Modal handlers
    setupModalHandlers();

    // Export handlers
    document.getElementById('exportPNG').addEventListener('click', () => {
        exportMapAsPNG();
    });

    document.getElementById('exportPDF').addEventListener('click', () => {
        alert('PDF export coming soon!');
    });
}

function setupModalHandlers() {
    // Save Preset Modal
    const saveModal = document.getElementById('savePresetModal');
    const confirmPresetBtn = document.getElementById('confirmPresetBtn');
    const cancelPresetBtn = document.getElementById('cancelPresetBtn');

    confirmPresetBtn.addEventListener('click', () => {
        const name = document.getElementById('presetName').value;
        const description = document.getElementById('presetDescription').value;

        if (!name) {
            alert('Please enter a preset name');
            return;
        }

        saveCustomPreset(name, description);
        saveModal.classList.remove('active');
        document.getElementById('presetName').value = '';
        document.getElementById('presetDescription').value = '';
    });

    cancelPresetBtn.addEventListener('click', () => {
        saveModal.classList.remove('active');
        document.getElementById('presetName').value = '';
        document.getElementById('presetDescription').value = '';
    });

    // Close modals when clicking close button
    document.querySelectorAll('.modal-close').forEach(button => {
        button.addEventListener('click', () => {
            button.closest('.modal').classList.remove('active');
        });
    });

    // Close modals when clicking outside
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
}

function showSavePresetModal() {
    document.getElementById('savePresetModal').classList.add('active');
}

function showExportModal() {
    document.getElementById('exportModal').classList.add('active');
}

// ===================================
// Utility Functions
// ===================================

function showLoading(show) {
    const loader = document.getElementById('loadingIndicator');
    if (show) {
        loader.classList.remove('hidden');
    } else {
        loader.classList.add('hidden');
    }
}

// ===================================
// Measurement Functions
// ===================================

function showMeasurementPanel() {
    document.getElementById('measurementPanel').classList.remove('hidden');
    document.getElementById('searchPanel').classList.add('hidden');

    if (!measurementLayer) {
        measurementLayer = L.featureGroup().addTo(map);
    }

    initMeasurementHandlers();
}

function initMeasurementHandlers() {
    if (measurementHandlersInitialized) {
        startMeasurement();
        return;
    }

    const measureDistance = document.getElementById('measureDistance');
    const measureArea = document.getElementById('measureArea');
    const closeMeasurement = document.getElementById('closeMeasurement');
    const clearMeasurement = document.getElementById('clearMeasurement');

    measureDistance.addEventListener('click', () => {
        currentMeasurementMode = 'distance';
        measureDistance.classList.add('active');
        measureArea.classList.remove('active');
        startMeasurement();
    });

    measureArea.addEventListener('click', () => {
        currentMeasurementMode = 'area';
        measureArea.classList.add('active');
        measureDistance.classList.remove('active');
        startMeasurement();
    });

    closeMeasurement.addEventListener('click', () => {
        document.getElementById('measurementPanel').classList.add('hidden');
        clearMeasurements();
    });

    clearMeasurement.addEventListener('click', () => {
        clearMeasurements();
    });

    measurementHandlersInitialized = true;

    // Start with distance measurement by default
    startMeasurement();
}

function startMeasurement() {
    clearMeasurements();

    const resultDiv = document.getElementById('measurementResult');
    resultDiv.innerHTML = '<p class="instruction">Click on map to start measuring</p>';

    if (currentMeasurementMode === 'distance') {
        startDistanceMeasurement();
    } else {
        startAreaMeasurement();
    }
}

function startDistanceMeasurement() {
    let points = [];
    let polyline = null;
    let markers = [];

    const clickHandler = (e) => {
        points.push(e.latlng);

        // Add marker
        const marker = L.circleMarker(e.latlng, {
            radius: 5,
            color: '#3388ff',
            fillColor: '#3388ff',
            fillOpacity: 1
        }).addTo(measurementLayer);
        markers.push(marker);

        // Draw line
        if (polyline) {
            measurementLayer.removeLayer(polyline);
        }

        if (points.length > 1) {
            polyline = L.polyline(points, {
                color: '#3388ff',
                weight: 3,
                dashArray: '5, 10'
            }).addTo(measurementLayer);

            // Calculate distance
            const distance = calculateTotalDistance(points);
            displayDistanceResult(distance);
        }
    };

    map.on('click', clickHandler);

    // Store handler for cleanup
    measurementLayer._clickHandler = clickHandler;
}

function startAreaMeasurement() {
    let points = [];
    let polygon = null;
    let markers = [];

    const clickHandler = (e) => {
        points.push(e.latlng);

        // Add marker
        const marker = L.circleMarker(e.latlng, {
            radius: 5,
            color: '#f357a1',
            fillColor: '#f357a1',
            fillOpacity: 1
        }).addTo(measurementLayer);
        markers.push(marker);

        // Draw polygon
        if (polygon) {
            measurementLayer.removeLayer(polygon);
        }

        if (points.length > 2) {
            polygon = L.polygon(points, {
                color: '#f357a1',
                weight: 3,
                fillOpacity: 0.2
            }).addTo(measurementLayer);

            // Calculate area
            const area = calculatePolygonArea(points);
            displayAreaResult(area);
        } else if (points.length === 2) {
            const tempLine = L.polyline(points, {
                color: '#f357a1',
                weight: 3,
                dashArray: '5, 10'
            }).addTo(measurementLayer);
        }
    };

    map.on('click', clickHandler);

    // Store handler for cleanup
    measurementLayer._clickHandler = clickHandler;
}

function calculateTotalDistance(points) {
    let total = 0;
    for (let i = 0; i < points.length - 1; i++) {
        total += points[i].distanceTo(points[i + 1]);
    }
    return total;
}

function calculatePolygonArea(points) {
    const polygon = L.polygon(points);
    // Convert to square meters using geodesic area calculation
    let area = 0;
    const coords = points.map(p => [p.lng, p.lat]);

    // Simple spherical excess formula for area calculation
    const R = 6378137; // Earth's radius in meters
    const toRad = Math.PI / 180;

    for (let i = 0; i < coords.length; i++) {
        const p1 = coords[i];
        const p2 = coords[(i + 1) % coords.length];
        area += (p2[0] - p1[0]) * toRad * (2 + Math.sin(p1[1] * toRad) + Math.sin(p2[1] * toRad));
    }

    area = Math.abs(area * R * R / 2);
    return area;
}

function displayDistanceResult(meters) {
    const km = meters / 1000;
    const miles = meters / 1609.34;
    const feet = meters * 3.28084;

    const resultDiv = document.getElementById('measurementResult');
    resultDiv.innerHTML = `
        <div class="result-item">
            <div class="result-label">Distance</div>
            <div class="result-value">${meters < 1000 ? meters.toFixed(2) + ' m' : km.toFixed(2) + ' km'}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Miles / Feet</div>
            <div class="result-value">${miles < 1 ? feet.toFixed(2) + ' ft' : miles.toFixed(2) + ' mi'}</div>
        </div>
    `;
}

function displayAreaResult(sqMeters) {
    const sqKm = sqMeters / 1000000;
    const acres = sqMeters / 4046.86;
    const sqMiles = sqMeters / 2589988;

    const resultDiv = document.getElementById('measurementResult');
    resultDiv.innerHTML = `
        <div class="result-item">
            <div class="result-label">Area</div>
            <div class="result-value">${sqMeters < 10000 ? sqMeters.toFixed(2) + ' m²' : sqKm.toFixed(2) + ' km²'}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Acres / Sq Miles</div>
            <div class="result-value">${acres < 640 ? acres.toFixed(2) + ' acres' : sqMiles.toFixed(2) + ' mi²'}</div>
        </div>
    `;
}

function clearMeasurements() {
    if (measurementLayer) {
        measurementLayer.clearLayers();

        // Remove click handler
        if (measurementLayer._clickHandler) {
            map.off('click', measurementLayer._clickHandler);
            measurementLayer._clickHandler = null;
        }
    }

    const resultDiv = document.getElementById('measurementResult');
    if (resultDiv) {
        resultDiv.innerHTML = '<p class="instruction">Click on map to start measuring</p>';
    }
}

// ===================================
// Search Functions
// ===================================

function showSearchPanel() {
    document.getElementById('searchPanel').classList.remove('hidden');
    document.getElementById('measurementPanel').classList.add('hidden');

    initSearchHandlers();
}

function initSearchHandlers() {
    if (searchHandlersInitialized) {
        return;
    }

    const searchInput = document.getElementById('searchInput');
    const searchSubmit = document.getElementById('searchSubmit');
    const closeSearch = document.getElementById('closeSearch');

    searchSubmit.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            searchLocation(query);
        }
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                searchLocation(query);
            }
        }
    });

    closeSearch.addEventListener('click', () => {
        document.getElementById('searchPanel').classList.add('hidden');
        clearSearchMarker();
    });

    searchHandlersInitialized = true;
}

async function searchLocation(query) {
    const searchLoading = document.getElementById('searchLoading');
    const searchResults = document.getElementById('searchResults');

    searchLoading.classList.remove('hidden');
    searchResults.classList.add('hidden');
    searchResults.innerHTML = '';

    try {
        // Use Nominatim (OpenStreetMap) geocoding service
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`,
            {
                headers: {
                    'User-Agent': 'Interactive Map Viewer'
                }
            }
        );

        if (!response.ok) {
            throw new Error('Search request failed');
        }

        const results = await response.json();

        searchLoading.classList.add('hidden');

        if (results.length === 0) {
            searchResults.innerHTML = '<p class="instruction">No results found. Try a different search.</p>';
            searchResults.classList.remove('hidden');
            return;
        }

        displaySearchResults(results);

    } catch (error) {
        console.error('Search error:', error);
        searchLoading.classList.add('hidden');
        searchResults.innerHTML = '<p class="instruction" style="color: var(--danger-color);">Search failed. Please try again.</p>';
        searchResults.classList.remove('hidden');
    }
}

function displaySearchResults(results) {
    const searchResults = document.getElementById('searchResults');

    searchResults.innerHTML = results.map((result, index) => `
        <div class="search-result-item" data-index="${index}" data-lat="${result.lat}" data-lon="${result.lon}">
            <div class="search-result-name">${result.display_name.split(',')[0]}</div>
            <div class="search-result-address">${result.display_name}</div>
        </div>
    `).join('');

    searchResults.classList.remove('hidden');

    // Add click handlers
    searchResults.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
            const lat = parseFloat(item.dataset.lat);
            const lon = parseFloat(item.dataset.lon);
            const name = item.querySelector('.search-result-name').textContent;

            zoomToLocation(lat, lon, name);
        });
    });
}

function zoomToLocation(lat, lon, name) {
    // Clear previous search marker
    clearSearchMarker();

    // Add new marker
    searchMarker = L.marker([lat, lon], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map);

    searchMarker.bindPopup(`<b>${name}</b>`).openPopup();

    // Zoom to location
    map.setView([lat, lon], 15, {
        animate: true,
        duration: 1
    });

    showSuccess(`Found: ${name}`);
}

function clearSearchMarker() {
    if (searchMarker) {
        map.removeLayer(searchMarker);
        searchMarker = null;
    }
}

function exportMapAsPNG() {
    const mapElement = document.getElementById('map');

    html2canvas(mapElement, {
        useCORS: true,
        allowTaint: true,
        logging: false
    }).then(canvas => {
        const link = document.createElement('a');
        link.download = `map-export-${new Date().getTime()}.png`;
        link.href = canvas.toDataURL();
        link.click();
    }).catch(error => {
        console.error('Export error:', error);
        alert('Error exporting map. Please try again.');
    });
}

// ===================================
// File Upload Functions
// ===================================

function setupFileUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadMessage = document.getElementById('uploadMessage');
    const progressFill = document.getElementById('progressFill');

    // Click to browse
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });

    // File selected via browse
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');

        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadMessage = document.getElementById('uploadMessage');
    const progressFill = document.getElementById('progressFill');

    // Validate file type
    const validExtensions = ['geojson', 'json', 'csv', 'kml', 'kmz'];
    const fileName = file.name.toLowerCase();
    const fileExtension = fileName.split('.').pop();

    if (!validExtensions.includes(fileExtension)) {
        alert(`Invalid file type. Supported formats: ${validExtensions.join(', ')}`);
        return;
    }

    // Show progress
    uploadStatus.classList.remove('hidden', 'success', 'error');
    uploadMessage.textContent = `Uploading ${file.name}...`;
    progressFill.style.width = '50%';

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok && result.success) {
            // Success
            progressFill.style.width = '100%';
            uploadStatus.classList.add('success');
            uploadMessage.textContent = `Success! Loaded ${result.feature_count} features from ${result.layer_name}`;

            // Add layer to map
            addUploadedLayer(result.layer_name, result.geojson);

            // Reset after 3 seconds
            setTimeout(() => {
                uploadStatus.classList.add('hidden');
                progressFill.style.width = '0%';
                fileInput.value = '';
            }, 3000);
        } else {
            // Error
            throw new Error(result.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        uploadStatus.classList.add('error');
        uploadMessage.textContent = `Error: ${error.message}`;
        progressFill.style.width = '0%';

        // Reset after 5 seconds
        setTimeout(() => {
            uploadStatus.classList.add('hidden');
            fileInput.value = '';
        }, 5000);
    }
}

function addUploadedLayer(layerName, geojson) {
    // Add to dataLayers
    dataLayers[layerName] = {
        name: layerName,
        display_name: layerName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        type: 'uploaded',
        data: geojson,
        visible: true
    };

    // Add to map
    addLayerToMap(layerName);
    currentState.layers.push(layerName);

    // Update layers list in UI
    const layersList = document.getElementById('layersList');
    const item = document.createElement('div');
    item.className = 'layer-item';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `layer-${layerName}`;
    checkbox.checked = true;
    checkbox.addEventListener('change', (e) => {
        toggleLayer(layerName, e.target.checked);
    });

    const icon = document.createElement('div');
    icon.className = 'layer-icon';
    icon.innerHTML = '<i class="fas fa-layer-group"></i>';

    const info = document.createElement('div');
    info.className = 'layer-info';
    info.innerHTML = `
        <div class="layer-name">${dataLayers[layerName].display_name}</div>
        <div class="layer-count">${geojson.features.length} features (uploaded)</div>
    `;

    item.appendChild(checkbox);
    item.appendChild(icon);
    item.appendChild(info);

    item.addEventListener('click', (e) => {
        if (e.target !== checkbox) {
            checkbox.checked = !checkbox.checked;
            toggleLayer(layerName, checkbox.checked);
        }
    });

    layersList.appendChild(item);

    // Update legend
    updateLegend();

    // Zoom to layer bounds
    if (layerGroups[layerName]) {
        map.fitBounds(layerGroups[layerName].getBounds(), { padding: [50, 50] });
    }
}

// ===================================
// Export Functions
// ===================================

function setupExportModal() {
    const exportBtn = document.getElementById('exportBtn');
    const exportModal = document.getElementById('exportModal');
    const exportLayerSelect = document.getElementById('exportLayerSelect');
    const exportMessage = document.getElementById('exportMessage');

    exportBtn.addEventListener('click', () => {
        // Populate layer dropdown
        exportLayerSelect.innerHTML = '<option value="">-- Select a layer --</option>';

        Object.keys(dataLayers).forEach(layerName => {
            if (dataLayers[layerName].visible) {
                const option = document.createElement('option');
                option.value = layerName;
                option.textContent = dataLayers[layerName].display_name;
                exportLayerSelect.appendChild(option);
            }
        });

        exportMessage.classList.add('hidden');
        showExportModal();
    });

    // Export GeoJSON
    document.getElementById('exportGeoJSON').addEventListener('click', async () => {
        const layerName = exportLayerSelect.value;
        if (!layerName) {
            showExportMessage('Please select a layer to export', 'error');
            return;
        }

        try {
            const layer = dataLayers[layerName];
            const geojson = layer.data;

            const response = await fetch('/api/export/geojson', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ geojson, layer_name: layerName })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `${layerName}.geojson`;
                link.click();
                window.URL.revokeObjectURL(url);

                showExportMessage('GeoJSON exported successfully!', 'success');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            showExportMessage('Error exporting GeoJSON', 'error');
        }
    });

    // Export KML
    document.getElementById('exportKML').addEventListener('click', async () => {
        const layerName = exportLayerSelect.value;
        if (!layerName) {
            showExportMessage('Please select a layer to export', 'error');
            return;
        }

        try {
            const layer = dataLayers[layerName];
            const geojson = layer.data;

            const response = await fetch('/api/export/kml', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ geojson, layer_name: layerName })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `${layerName}.kml`;
                link.click();
                window.URL.revokeObjectURL(url);

                showExportMessage('KML exported successfully!', 'success');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            showExportMessage('Error exporting KML', 'error');
        }
    });

    // Export CSV
    document.getElementById('exportCSV').addEventListener('click', async () => {
        const layerName = exportLayerSelect.value;
        if (!layerName) {
            showExportMessage('Please select a layer to export', 'error');
            return;
        }

        try {
            const layer = dataLayers[layerName];
            const geojson = layer.data;

            const response = await fetch('/api/export/csv', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ geojson, layer_name: layerName })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `${layerName}.csv`;
                link.click();
                window.URL.revokeObjectURL(url);

                showExportMessage('CSV exported successfully!', 'success');
            } else {
                const result = await response.json();
                throw new Error(result.error || 'Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            showExportMessage(`Error: ${error.message}`, 'error');
        }
    });
}

function showExportMessage(message, type) {
    const exportMessage = document.getElementById('exportMessage');
    exportMessage.textContent = message;
    exportMessage.className = `export-message ${type}`;
    exportMessage.classList.remove('hidden');

    if (type === 'success') {
        setTimeout(() => {
            exportMessage.classList.add('hidden');
        }, 3000);
    }
}

// Initialize upload and export on page load
document.addEventListener('DOMContentLoaded', () => {
    setupFileUpload();
    setupExportModal();
});

// Add CSS for pulsing animation and dynamic styles
const dynamicStyle = document.createElement('style');
dynamicStyle.id = 'dynamic-marker-styles';
updateMarkerStyles();
document.head.appendChild(dynamicStyle);

function updateMarkerStyles() {
    const fontSize = currentState.fontSize === 'small' ? '10px' : currentState.fontSize === 'large' ? '14px' : '12px';
    dynamicStyle.textContent = `
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7); }
            50% { box-shadow: 0 0 0 10px rgba(255, 255, 255, 0); }
        }

        .marker-label {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            font-weight: 600;
            font-size: ${fontSize};
            color: #2c3e50;
            text-shadow: 1px 1px 2px white, -1px -1px 2px white, 1px -1px 2px white, -1px 1px 2px white;
        }

        .leaflet-popup-content {
            font-size: ${fontSize};
        }

        .legend {
            font-size: ${fontSize};
        }
    `;
}

// ===================================
// Sidebar Resize Functionality
// ===================================

function initSidebarResize() {
    const resizeHandle = document.getElementById('resizeHandle');
    const controlPanel = document.getElementById('controlPanel');
    let isResizing = false;
    let startX = 0;
    let startWidth = 0;

    // Debounced map resize for better performance
    const debouncedMapResize = debounce(() => {
        if (map) {
            map.invalidateSize();
        }
    }, 100);

    // Throttled resize for smoother visual updates
    const throttledResize = throttle((width) => {
        controlPanel.style.width = width + 'px';
        debouncedMapResize();
    }, 16); // ~60fps

    resizeHandle.addEventListener('mousedown', (e) => {
        isResizing = true;
        startX = e.clientX;
        startWidth = controlPanel.offsetWidth;

        resizeHandle.classList.add('active');
        controlPanel.classList.add('resizing');
        document.body.style.cursor = 'ew-resize';
        document.body.style.userSelect = 'none';

        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;

        const width = startWidth + (e.clientX - startX);
        const minWidth = 280;
        const maxWidth = 800;

        if (width >= minWidth && width <= maxWidth) {
            throttledResize(width);
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            resizeHandle.classList.remove('active');
            controlPanel.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';

            // Final resize to ensure accuracy
            if (map) {
                map.invalidateSize();
            }
        }
    });
}

// Initialize resize and keyboard shortcuts on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    initSidebarResize();
    initKeyboardShortcuts();
});

console.log('Interactive Map Viewer initialized successfully!');
