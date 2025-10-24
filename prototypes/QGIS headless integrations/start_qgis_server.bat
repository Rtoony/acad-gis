@echo off
REM ============================================
REM ACAD=GIS Server Launcher with QGIS Support
REM ============================================

echo.
echo ========================================
echo ACAD=GIS Server with QGIS
echo ========================================
echo.

REM Set QGIS installation paths (OSGeo4W)
REM Adjust this path if QGIS is installed elsewhere
set OSGEO4W_ROOT=C:\OSGeo4W64

REM Check if QGIS exists
if not exist "%OSGEO4W_ROOT%" (
    echo ERROR: QGIS not found at %OSGEO4W_ROOT%
    echo.
    echo Please install QGIS from https://qgis.org
    echo Or update OSGEO4W_ROOT variable in this script
    echo.
    pause
    exit /b 1
)

REM Set QGIS paths
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT%\apps\qgis
set PYTHONPATH=%QGIS_PREFIX_PATH%\python;%PYTHONPATH%
set PYTHONPATH=%QGIS_PREFIX_PATH%\python\plugins;%PYTHONPATH%

REM Set Qt plugin path
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\Qt5\plugins
set QT_PLUGIN_PATH=%QGIS_PREFIX_PATH%\qtplugins;%QT_PLUGIN_PATH%

REM Add QGIS and GDAL binaries to PATH
set PATH=%QGIS_PREFIX_PATH%\bin;%PATH%
set PATH=%OSGEO4W_ROOT%\bin;%PATH%

REM Set GDAL data
set GDAL_DATA=%OSGEO4W_ROOT%\share\gdal
set PROJ_LIB=%OSGEO4W_ROOT%\share\proj

echo QGIS Configuration:
echo   QGIS_PREFIX_PATH = %QGIS_PREFIX_PATH%
echo   PYTHONPATH       = %PYTHONPATH%
echo   QT_PLUGIN_PATH   = %QT_PLUGIN_PATH%
echo.

REM Test QGIS Python availability
echo Testing QGIS Python environment...
python -c "from qgis.core import QgsApplication; print('  OK: QGIS Python available')" 2>nul
if errorlevel 1 (
    echo   ERROR: QGIS Python modules not found
    echo   Check QGIS installation and paths
    pause
    exit /b 1
)
echo.

REM Launch server with QGIS-enabled Python
echo Starting ACAD=GIS API Server with GIS support...
echo.
echo Press Ctrl+C to stop the server
echo.
python api_server.py

pause
