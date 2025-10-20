"""
Quick Test with New Password: uhY8zzuy4wLbAFBC
"""

import psycopg2

print("=" * 70)
print("TESTING NEW PASSWORD")
print("=" * 70)
print()

host = 'aws-1-us-east-2.pooler.supabase.com'
port = '5432'
database = 'postgres'
password = 'uhY8zzuy4wLbAFBC'

# Try both user formats
users = [
    'postgres.dkvyhbqmeumanhnhxmxf',
    'postgres'
]

for user in users:
    print(f"Trying user: {user}")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10,
            sslmode='prefer'
        )
        
        print(f"✅✅✅ SUCCESS!!!")
        print()
        
        cur = conn.cursor()
        
        # Get table count
        cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = cur.fetchone()[0]
        print(f"✅ Found {table_count} tables in database")
        
        # Try to get projects
        try:
            cur.execute("SELECT COUNT(*) FROM projects")
            project_count = cur.fetchone()[0]
            print(f"✅ Found {project_count} projects")
        except Exception as e:
            print(f"ℹ️  Projects table: {str(e)[:50]}")
        
        # Try to get drawings
        try:
            cur.execute("SELECT COUNT(*) FROM drawings")
            drawing_count = cur.fetchone()[0]
            print(f"✅ Found {drawing_count} drawings")
        except Exception as e:
            print(f"ℹ️  Drawings table: {str(e)[:50]}")
        
        cur.close()
        conn.close()
        
        print()
        print("=" * 70)
        print("SUCCESS! Update your .env file with:")
        print("=" * 70)
        print(f"DB_HOST={host}")
        print(f"DB_PORT={port}")
        print(f"DB_NAME={database}")
        print(f"DB_USER={user}")
        print(f"DB_PASSWORD={password}")
        print("=" * 70)
        
        exit(0)
        
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}")
        print()

print()
print("=" * 70)
print("Both formats failed. Possible issues:")
print("=" * 70)
print("1. Password hasn't propagated yet (wait 2 minutes)")
print("2. Project is paused (check dashboard)")
print("3. Wrong project (verify URL)")
print()
