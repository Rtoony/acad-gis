"""
Simple migration runner for ACAD-GIS.

Usage:
    python run_migrations.py

Reads *.sql files from backend/migrations in lexical order and executes them
against the configured database (see backend/.env). Each file should be
idempotent.
"""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))
    from database import get_db_connection  # type: ignore
else:
    from .database import get_db_connection  # type: ignore


def run():
    migrations_dir = Path(__file__).parent / "migrations"
    if not migrations_dir.exists():
        print("No migrations directory found; nothing to run.")
        return

    files = sorted(p for p in migrations_dir.glob("*.sql"))
    if not files:
        print("No migration files discovered.")
        return

    print(f"Running {len(files)} migration(s)...")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for path in files:
                sql = path.read_text()
                print(f"  → {path.name}")
                cur.execute(sql)
    print("✅ Migrations complete.")


if __name__ == "__main__":
    run()
