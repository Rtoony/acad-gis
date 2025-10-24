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
        print("❌ No migrations directory found; nothing to run.")
        return

    files = sorted(p for p in migrations_dir.glob("*.sql"))
    if not files:
        print("⚠️  No migration files discovered.")
        return

    print("=" * 60)
    print("🚀 ACAD-GIS Database Migration Runner")
    print("=" * 60)
    print(f"\n📋 Found {len(files)} migration file(s):")
    for f in files:
        print(f"   - {f.name}")

    print(f"\n🔄 Applying migrations to database...")

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for path in files:
                    sql = path.read_text()
                    print(f"  📄 Applying: {path.name}...", end=" ")
                    cur.execute(sql)
                    print("✅")
        print("\n" + "=" * 60)
        print("🎉 All migrations completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Migration failed!")
        print(f"   Error: {str(e)}")
        print("\n" + "=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    run()
