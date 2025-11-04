"""
Testing Database Operations
Tests: Connection, queries, data integrity
"""

import psycopg2
from dotenv import load_dotenv
import os

# Load database credentials from backend/.env
load_dotenv("backend/.env")


def get_db_connection():
    """
    Helper function to connect to database
    """
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        connect_timeout=10
    )


def test_database_connection():
    """
    Test we can connect to the database
    """
    conn = get_db_connection()
    assert conn is not None

    cur = conn.cursor()
    cur.execute("SELECT 1")
    result = cur.fetchone()

    assert result[0] == 1

    cur.close()
    conn.close()

    print("✅ Database connection works")


def test_projects_table_exists():
    """
    Test that the projects table exists
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if projects table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'projects'
        )
    """)

    exists = cur.fetchone()[0]
    assert exists == True

    cur.close()
    conn.close()

    print("✅ Projects table exists")


def test_drawings_table_exists():
    """
    Test that the drawings table exists
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'drawings'
        )
    """)

    exists = cur.fetchone()[0]
    assert exists == True

    cur.close()
    conn.close()

    print("✅ Drawings table exists")


def test_can_query_projects():
    """
    Test we can query projects from database
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM projects")
    count = cur.fetchone()[0]

    # Count should be a number (even if 0)
    assert isinstance(count, int)
    assert count >= 0

    cur.close()
    conn.close()

    print(f"✅ Database has {count} projects")


def test_can_query_drawings():
    """
    Test we can query drawings from database
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM drawings")
    count = cur.fetchone()[0]

    assert isinstance(count, int)
    assert count >= 0

    cur.close()
    conn.close()

    print(f"✅ Database has {count} drawings")


def test_postgis_installed():
    """
    Test that PostGIS extension is installed
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT EXISTS (
            SELECT FROM pg_extension
            WHERE extname = 'postgis'
        )
    """)

    has_postgis = cur.fetchone()[0]
    assert has_postgis == True

    cur.close()
    conn.close()

    print("✅ PostGIS is installed")


def test_uuid_extension_installed():
    """
    Test that uuid-ossp extension is installed
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT EXISTS (
            SELECT FROM pg_extension
            WHERE extname = 'uuid-ossp'
        )
    """)

    has_uuid = cur.fetchone()[0]
    assert has_uuid == True

    cur.close()
    conn.close()

    print("✅ UUID extension is installed")


def test_canonical_features_table_exists():
    """
    Test that canonical features table exists (for GIS data)
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'canonical_features'
        )
    """)

    exists = cur.fetchone()[0]
    assert exists == True

    cur.close()
    conn.close()

    print("✅ Canonical features table exists")
