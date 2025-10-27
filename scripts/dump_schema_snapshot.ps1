<#
  Dump the database schema (DDL only) to docs/DATABASE_SCHEMA_SNAPSHOT.sql

  Usage (PowerShell):
    # Set connection via environment or inline
    $env:PGHOST = "localhost"
    $env:PGPORT = "5432"
    $env:PGUSER = "postgres"
    $env:PGDATABASE = "acad_gis"
    # Optional: PGPASSWORD should be set in env or use .pgpass

    pwsh -File scripts/dump_schema_snapshot.ps1

  Notes:
    - Requires PostgreSQL client tools (`pg_dump`) in PATH.
    - Writes/overwrites docs/DATABASE_SCHEMA_SNAPSHOT.sql relative to repo root.
#>

param(
  [string]$Host = $env:PGHOST,
  [string]$Port = $env:PGPORT,
  [string]$User = $env:PGUSER,
  [string]$Db   = $env:PGDATABASE
)

if (-not $Host) { $Host = "localhost" }
if (-not $Port) { $Port = "5432" }
if (-not $User) { $User = "postgres" }
if (-not $Db)   { $Db   = "acad_gis" }

$RepoRoot = Split-Path -Parent $PSScriptRoot
$OutFile  = Join-Path $RepoRoot "docs/DATABASE_SCHEMA_SNAPSHOT.sql"

Write-Host "Dumping schema for '$Db' on $Host:$Port as $User..." -ForegroundColor Cyan

$pgDumpArgs = @(
  "--schema-only",
  "--no-owner",
  "--no-privileges",
  "--if-exists",
  "-h", $Host,
  "-p", $Port,
  "-U", $User,
  $Db
)

try {
  $start = Get-Date
  $dump = & pg_dump @pgDumpArgs 2>&1
  if ($LASTEXITCODE -ne 0) {
    Write-Error "pg_dump failed:`n$dump"
    exit $LASTEXITCODE
  }
  Set-Content -Path $OutFile -Value "-- Reference DDL Snapshot (auto-generated) `n-- Generated: $(Get-Date -Format o)`n`n$dump" -Encoding UTF8
  $elapsed = (Get-Date) - $start
  Write-Host "Wrote schema snapshot to $OutFile in $([int]$elapsed.TotalSeconds)s" -ForegroundColor Green
} catch {
  Write-Error $_.Exception.Message
  exit 1
}

