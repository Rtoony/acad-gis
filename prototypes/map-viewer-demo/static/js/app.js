/**
 * Interactive Map Viewer Application
 * Main JavaScript file for map functionality and UI controls
 */

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
                const data = await dataResponse.json();
                dataLayers[layer.name] = {
                    ...layer,
                    data: data,
                    visible: false
                };
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

    // Initialize marker cluster group
    markerClusterGroup = L.markerClusterGroup({
        maxClusterRadius: 50,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: true,
        zoomToBoundsOnClick: true
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
            url: 'https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg',
            attribution: 'Map tiles by Stamen Design, under CC BY 3.0',
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
            name: 'Dark Matter',
            url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            icon: 'fa-circle'
        },
        natgeo: {
            name: 'National Geographic',
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
            attribution: 'Esri, National Geographic',
            icon: 'fa-globe-americas'
        },
        positron: {
            name: 'Positron (Clean)',
            url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            icon: 'fa-lightbulb'
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
        { id: 'darkmatter', name: 'Dark Matter', icon: 'fa-circle' },
        { id: 'natgeo', name: 'National Geographic', icon: 'fa-globe-americas' },
        { id: 'positron', name: 'Positron (Clean)', icon: 'fa-lightbulb' },
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
        if (!map.hasLayer(measureControl)) {
            map.addControl(measureControl);
        }
        alert('Click on the map to start measuring. Use the drawing tools in the top-left corner.');
    });

    document.getElementById('searchBtn').addEventListener('click', () => {
        const query = prompt('Enter location to search:');
        if (query) {
            searchLocation(query);
        }
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

async function searchLocation(query) {
    // Simple implementation - in production, you'd use a geocoding service
    alert(`Search functionality would find: ${query}\n(Geocoding service integration needed)`);
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
            controlPanel.style.width = width + 'px';
            // Trigger map resize
            if (map) {
                setTimeout(() => map.invalidateSize(), 0);
            }
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            resizeHandle.classList.remove('active');
            controlPanel.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
}

// Initialize resize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    initSidebarResize();
});

console.log('Interactive Map Viewer initialized successfully!');
