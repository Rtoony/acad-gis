import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'sslmode': 'prefer',
    'connect_timeout': 10,
}

print("DB_CONFIG being passed to psycopg2:")
for key, value in DB_CONFIG.items():
    if key == 'password':
        print(f"  {key}: {value[:5]}...")
    else:
        print(f"  {key}: {value}")

print("\nAttempting connection...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ Connected!")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
