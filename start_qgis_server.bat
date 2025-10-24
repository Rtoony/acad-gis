@echo off
setlocal enableextensions

REM ==== CONFIGURE YOUR QGIS INSTALL ROOT ====
set "QGIS_ROOT=C:\Program Files\QGIS 3.40.11"
set "QGIS_APP=%QGIS_ROOT%\apps\qgis-ltr"
set "QGIS_PYHOME=%QGIS_ROOT%\Python312"
set "QGIS_QT=%QGIS_ROOT%\Qt5"

REM ==== VALIDATE REQUIRED FOLDERS ====
if not exist "%QGIS_ROOT%" echo [ERROR] QGIS_ROOT not found: "%QGIS_ROOT%" & goto FAIL
if not exist "%QGIS_APP%" echo [ERROR] QGIS_APP not found: "%QGIS_APP%" & goto FAIL
if not exist "%QGIS_PYHOME%" echo [WARN] QGIS_PYHOME not found: "%QGIS_PYHOME%". Adjust if needed.

REM ==== CORE ENV FOR PYQGIS ====
set "QGIS_PREFIX_PATH=%QGIS_APP%"
set "PYTHONPATH=%QGIS_APP%\python;%QGIS_PYHOME%\Lib;%QGIS_PYHOME%\Lib\site-packages"
set "PATH=%QGIS_ROOT%\bin;%QGIS_APP%\bin;%QGIS_QT%\bin;%QGIS_PYHOME%;%PATH%"
set "GDAL_DATA=%QGIS_ROOT%\share\gdal"
set "QT_PLUGIN_PATH=%QGIS_QT%\plugins;%QGIS_APP%\qtplugins"

REM ==== PICK PYTHON (prefer QGIS-bundled) ====
set "PYBIN=%QGIS_PYHOME%\python.exe"
if not exist "%PYBIN%" set "PYBIN=%QGIS_ROOT%\bin\python-qgis-ltr.bat"
if not exist "%PYBIN%" set "PYBIN=python"

echo [INFO] Using Python: "%PYBIN%"

REM ==== DIAGNOSTICS ====
call "%PYBIN%" -c "import sys; print('python exe:', sys.executable)" || goto FAIL
call "%PYBIN%" -c "import PyQt5, qgis; print('QGIS imported OK')" || goto FAIL

REM ==== PICK INTERPRETER FOR UVICORN ====
set "UVIPY=%PYBIN%"
call "%UVIPY%" -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
  REM Try the Windows Python launcher (system Python)
  where py >nul 2>&1 && (
    py -3 -c "import uvicorn" >nul 2>&1
    if not errorlevel 1 (
      set "UVIPY=py -3"
    ) else (
      set "UVIPY=py"
    )
  )
)
echo [INFO] Using uvicorn via: "%UVIPY%"

REM If using a non-QGIS interpreter for uvicorn, ensure it still sees PyQGIS
if /I not "%UVIPY%"=="%PYBIN%" (
  if /I "%UVIPY:~0,2%"=="py" (
    call %UVIPY% -c "import PyQt5, qgis; print('Chosen uvicorn interpreter can import QGIS')" || goto FAIL
  ) else (
    call "%UVIPY%" -c "import PyQt5, qgis; print('Chosen uvicorn interpreter can import QGIS')" || goto FAIL
  )
)

REM ==== START SERVER ====
pushd "%~dp0backend" || goto FAIL
if /I "%UVIPY:~0,2%"=="py" (
  call %UVIPY% -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
) else (
  call "%UVIPY%" -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
)
popd

goto :EOF

:FAIL
pause
exit /b 1
