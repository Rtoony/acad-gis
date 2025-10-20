"""
Connection Troubleshooter - Try Different Credential Formats
This will test different variations to find what works
"""

import psycopg2

print("=" * 70)
print("TESTING DIFFERENT CONNECTION FORMATS")
print("=" * 70)
print()

# Your confirmed details
host = 'aws-1-us-east-2.pooler.supabase.com'
port = '5432'
database = 'postgres'
password = 'cNeT9bcpsnLFqubV'
project_ref = 'dkvyhbqmeumanhnhxmxf'

# Try different user formats
user_formats = [
    ('Format 1', f'postgres.{project_ref}'),
    ('Format 2', f'postgres'),
    ('Format 3', f'{project_ref}'),
]

print(f"Testing host: {host}")
print(f"Testing port: {port}")
print(f"Testing password: {'*' * len(password)}")
print()

for name, user in user_formats:
    print(f"Trying {name}: {user}")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=5,
            sslmode='prefer'
        )
        
        print(f"  ✅✅✅ SUCCESS! This format works!")
        
        # Get some info
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = cur.fetchone()[0]
        print(f"  ✅ Found {table_count} tables")
        
        try:
            cur.execute("SELECT COUNT(*) FROM projects")
            project_count = cur.fetchone()[0]
            print(f"  ✅ Found {project_count} projects")
        except:
            print(f"  ℹ️  Projects table not found (might be empty database)")
        
        cur.close()
        conn.close()
        
        print()
        print("=" * 70)
        print("WINNER! Use this in your .env file:")
        print("=" * 70)
        print(f"DB_HOST={host}")
        print(f"DB_PORT={port}")
        print(f"DB_NAME={database}")
        print(f"DB_USER={user}")
        print(f"DB_PASSWORD={password}")
        print("=" * 70)
        exit(0)
        
    except psycopg2.OperationalError as e:
        error_str = str(e)
        if "password authentication failed" in error_str:
            print(f"  ❌ Wrong password for this user format")
        elif "timeout" in error_str.lower():
            print(f"  ⏱️  Timeout (might still be connecting)")
        elif "does not exist" in error_str:
            print(f"  ❌ User doesn't exist in this format")
        else:
            print(f"  ❌ Failed: {error_str[:60]}...")
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:60]}...")
    
    print()

print()
print("=" * 70)
print("❌ NONE OF THE FORMATS WORKED")
print("=" * 70)
print()
print("This means either:")
print("  1. Password is wrong (double-check in Supabase)")
print("  2. Password reset hasn't propagated (wait 5 more minutes)")
print("  3. Project is paused (check dashboard)")
print()
print("Next steps:")
print("  1. Go to: https://supabase.com/dashboard/project/dkvyhbqmeumanhnhxmxf")
print("  2. Check if project shows 'Paused' - if so, click 'Resume'")
print("  3. Go to Settings → Database → Connection String")
print("  4. Copy the EXACT connection string and share it")
print()
