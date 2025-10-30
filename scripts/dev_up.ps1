<#
Dev bring-up: PostGIS + API + smoke test

Usage:
  pwsh -File scripts/dev_up.ps1

Requirements:
  - Docker Desktop
  - Python 3.10+
#>

param(
  [string]$ApiHost = "http://localhost:8000",
  [switch]$NoDocker
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-Command($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    throw "Required command '$name' not found in PATH."
  }
}

function Wait-For-Url($url, [int]$retries = 60, [int]$delayMs = 1000) {
  for ($i=0; $i -lt $retries; $i++) {
    try {
      $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
      if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) { return $true }
    } catch { }
    Start-Sleep -Milliseconds $delayMs
  }
  return $false
}

function Wait-For-ContainerHealthy($name, [int]$retries = 60, [int]$delayMs = 1000) {
  for ($i=0; $i -lt $retries; $i++) {
    try {
      $status = docker inspect --format '{{.State.Health.Status}}' $name 2>$null
      if ($LASTEXITCODE -eq 0 -and $status.Trim() -eq 'healthy') { return $true }
    } catch { }
    Start-Sleep -Milliseconds $delayMs
  }
  return $false
}

Write-Host "== Dev bring-up: PostGIS + API + Smoke Test ==" -ForegroundColor Cyan

if (-not $NoDocker) {
  Ensure-Command docker

  Write-Host "- Starting PostGIS via docker compose..." -ForegroundColor Yellow
  docker compose -f docker/docker-compose.postgis.yml up -d

  Write-Host "- Waiting for DB container to be healthy..." -ForegroundColor Yellow
  if (-not (Wait-For-ContainerHealthy -name 'acad_gis_postgis' -retries 120 -delayMs 1000)) {
    throw "Database container did not become healthy in time."
  }
}

Ensure-Command python

# Create backend/.env if missing
$envPath = Join-Path $PSScriptRoot '..' 'backend' '.env'
if (-not (Test-Path $envPath)) {
  Write-Host "- Creating backend/.env from example..." -ForegroundColor Yellow
  Copy-Item (Join-Path $PSScriptRoot '..' 'backend' '.env.example') $envPath -Force
}

# Create virtual env and install deps
$venv = Join-Path $PSScriptRoot '..' '.venv'
if (-not (Test-Path $venv)) {
  Write-Host "- Creating virtual environment (.venv)..." -ForegroundColor Yellow
  python -m venv $venv
}

$venvPython = Join-Path $venv 'Scripts' 'python.exe'
if (-not (Test-Path $venvPython)) { $venvPython = Join-Path $venv 'bin' 'python' }
if (-not (Test-Path $venvPython)) { throw "Python not found in venv." }

Write-Host "- Installing backend requirements..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip >$null
& $venvPython -m pip install -r (Join-Path $PSScriptRoot '..' 'backend' 'requirements.txt')

Write-Host "- Running migrations..." -ForegroundColor Yellow
& $venvPython (Join-Path $PSScriptRoot '..' 'backend' 'run_migrations.py')

Write-Host "- Starting API server..." -ForegroundColor Yellow
$apiScript = Join-Path $PSScriptRoot '..' 'backend' 'api_server.py'
$proc = Start-Process -FilePath $venvPython -ArgumentList @($apiScript) -PassThru -WindowStyle Hidden

try {
  Write-Host "- Waiting for API to be ready at $ApiHost/api/health ..." -ForegroundColor Yellow
  if (-not (Wait-For-Url "$ApiHost/api/health" 120 1000)) {
    throw "API did not become ready in time."
  }

  Write-Host "- Running smoke test..." -ForegroundColor Yellow
  $env:API_BASE_URL = $ApiHost
  & $venvPython (Join-Path $PSScriptRoot 'smoke_test_survey_civil.py')
  if ($LASTEXITCODE -ne 0) { throw "Smoke test reported failure ($LASTEXITCODE)." }

  Write-Host "== SUCCESS: Smoke test PASS ==" -ForegroundColor Green
}
finally {
  Write-Host "- Stopping API server..." -ForegroundColor Yellow
  if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force }
}

