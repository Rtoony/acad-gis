import psycopg2

DB_CONFIG = {
    'host': 'aws-1-us-east-2.pooler.supabase.com',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres.dkvyhbqmeumanhnhxmxf',
    'password': 'FFj9aBq8PtYNPaiz',
    'sslmode': 'prefer',
    'connect_timeout': 10,
}

print("Testing OLD password...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ OLD PASSWORD WORKS!")
    conn.close()
except Exception as e:
    print(f"❌ Old password failed: {e}")

DB_CONFIG['password'] = 'uhY8zzuy4wLbAFBC'
print("\nTesting NEW password...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ NEW PASSWORD WORKS!")
    conn.close()
except Exception as e:
    print(f"❌ New password failed: {e}")
