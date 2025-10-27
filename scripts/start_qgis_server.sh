#!/usr/bin/env bash
# Launch ACAD-GIS API server with QGIS environment variables (Linux/WSL/macOS).
# Adjust QGIS_PREFIX_PATH as needed for your platform.

set -euo pipefail

QGIS_PREFIX_PATH="${QGIS_PREFIX_PATH:-/usr}"
export QGIS_PREFIX_PATH
export PATH="$QGIS_PREFIX_PATH/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pushd "$SCRIPT_DIR/backend" >/dev/null
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
popd >/dev/null
