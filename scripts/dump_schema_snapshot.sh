#!/usr/bin/env bash
set -euo pipefail

# Dump the database schema (DDL only) to docs/DATABASE_SCHEMA_SNAPSHOT.sql
# Usage (bash):
#   export PGHOST=localhost PGPORT=5432 PGUSER=postgres PGDATABASE=acad_gis
#   bash scripts/dump_schema_snapshot.sh
# Notes:
#   - Requires PostgreSQL client tools (`pg_dump`) in PATH.
#   - Writes/overwrites docs/DATABASE_SCHEMA_SNAPSHOT.sql relative to repo root.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_FILE="$REPO_ROOT/docs/DATABASE_SCHEMA_SNAPSHOT.sql"

HOST="${PGHOST:-localhost}"
PORT="${PGPORT:-5432}"
USER="${PGUSER:-postgres}"
DB="${PGDATABASE:-acad_gis}"

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "pg_dump not found in PATH" >&2
  exit 127
fi

echo "Dumping schema for '$DB' on $HOST:$PORT as $USER..."
start_ts=$(date +%s)
{
  echo "-- Reference DDL Snapshot (auto-generated)"
  echo "-- Generated: $(date -Iseconds)"
  echo
  pg_dump \
    --schema-only \
    --no-owner \
    --no-privileges \
    --if-exists \
    -h "$HOST" \
    -p "$PORT" \
    -U "$USER" \
    "$DB"
} > "$OUT_FILE"

elapsed=$(( $(date +%s) - start_ts ))
echo "Wrote schema snapshot to $OUT_FILE in ${elapsed}s"

