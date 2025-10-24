#!/bin/bash
# ============================================
# ACAD=GIS Server Launcher with QGIS Support
# ============================================

echo ""
echo "========================================"
echo "ACAD=GIS Server with QGIS"
echo "========================================"
echo ""

# Detect QGIS installation
if [ -d "/usr/share/qgis" ]; then
    # Standard Linux installation
    export QGIS_PREFIX_PATH=/usr
    export PYTHONPATH=/usr/share/qgis/python:$PYTHONPATH
    export LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH
    echo "✓ Found QGIS at /usr"
elif [ -d "/Applications/QGIS.app" ]; then
    # macOS installation
    export QGIS_PREFIX_PATH=/Applications/QGIS.app/Contents/MacOS
    export PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python:$PYTHONPATH
    export DYLD_LIBRARY_PATH=/Applications/QGIS.app/Contents/MacOS/lib:$DYLD_LIBRARY_PATH
    echo "✓ Found QGIS at /Applications/QGIS.app"
else
    echo "ERROR: QGIS not found"
    echo ""
    echo "Please install QGIS:"
    echo "  Ubuntu/Debian: sudo apt install qgis python3-qgis"
    echo "  Fedora:        sudo dnf install qgis python3-qgis"
    echo "  macOS:         brew install qgis"
    echo ""
    exit 1
fi

echo "QGIS Configuration:"
echo "  QGIS_PREFIX_PATH = $QGIS_PREFIX_PATH"
echo "  PYTHONPATH       = $PYTHONPATH"
echo ""

# Test QGIS Python availability
echo "Testing QGIS Python environment..."
python3 -c "from qgis.core import QgsApplication; print('  ✓ QGIS Python available')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  ✗ ERROR: QGIS Python modules not found"
    echo "  Check QGIS installation"
    exit 1
fi
echo ""

# Launch server
echo "Starting ACAD=GIS API Server with GIS support..."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 api_server.py
