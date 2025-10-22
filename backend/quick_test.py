"""
Quick Connection Test - 2 Minutes
Run this to verify your database connection works
"""

import psycopg2
from dotenv import load_dotenv
import os

print("=" * 70)
print("ACAD=GIS Connection Test")
print("=" * 70)
print()

# Load .env file
print("Step 1: Loading .env file...")
load_dotenv()

# Show what was loaded (hide password)
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

print(f"  DB_HOST: {db_host}")
print(f"  DB_PORT: {db_port}")
print(f"  DB_NAME: {db_name}")
print(f"  DB_USER: {db_user}")
print(f"  DB_PASSWORD: {'*' * len(db_password) if db_password else 'NOT SET!'}")
print()

# Check if all values loaded
if not all([db_host, db_port, db_name, db_user, db_password]):
    print("❌ ERROR: Some environment variables are missing!")
    print("   Make sure .env file is in the same directory as this script")
    exit(1)

print("✅ All environment variables loaded")
print()

# Test connection
print("Step 2: Testing database connection...")
try:
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password,
        connect_timeout=10,
        sslmode='prefer'
    )
    
    print("✅ CONNECTION SUCCESSFUL!")
    print()
    
    # Get some info
    cur = conn.cursor()
    
    # PostgreSQL version
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"✅ PostgreSQL: {version[:60]}...")
    print()
    
    # Count projects
    try:
        cur.execute("SELECT COUNT(*) FROM projects")
        project_count = cur.fetchone()[0]
        print(f"✅ Found {project_count} projects in database")
    except:
        print("⚠️  Could not count projects (table might not exist yet)")
    
    # Count drawings
    try:
        cur.execute("SELECT COUNT(*) FROM drawings")
        drawing_count = cur.fetchone()[0]
        print(f"✅ Found {drawing_count} drawings in database")
    except:
        print("⚠️  Could not count drawings (table might not exist yet)")
    
    # Count block definitions
    try:
        cur.execute("SELECT COUNT(*) FROM block_definitions")
        block_count = cur.fetchone()[0]
        print(f"✅ Found {block_count} symbols in database")
    except:
        print("⚠️  Could not count symbols (table might not exist yet)")
    
    cur.close()
    conn.close()
    
    print()
    print("=" * 70)
    print("✅ TEST PASSED! Your database is connected and working.")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Start your API server:")
    print("     python api_server.py")
    print()
    print("  2. Refresh your browser:")
    print("     file:///H:/acad-gis/tool_launcher.html")
    print()
    
except psycopg2.OperationalError as e:
    print("❌ CONNECTION FAILED!")
    print()
    error_msg = str(e)
    
    if "password authentication failed" in error_msg:
        print("Problem: Wrong password")
        print("Solution: Check your password in Supabase dashboard")
        print("          Settings → Database → Reset password")
    elif "timeout" in error_msg.lower():
        print("Problem: Connection timeout")
        print("Solution: Check if Supabase project is paused")
        print("          Go to dashboard and click 'Resume'")
    elif "could not translate host name" in error_msg.lower():
        print("Problem: Cannot reach database host")
        print("Solution: Check DB_HOST in .env file")
        print(f"          Should be: aws-1-us-east-2.pooler.supabase.com")
    else:
        print(f"Error: {error_msg}")
    
    print()
    exit(1)

except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {str(e)}")
    exit(1)
