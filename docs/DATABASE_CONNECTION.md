# Supabase Database Connection Guide

**Created:** October 19, 2025  
**Critical:** This documents the specific Supabase connection quirks for ACAD-GIS

---

## The IPv6 Problem

### Why Direct Connection Fails

**Supabase free tier behavior:**
- Direct connections use IPv6-only hostnames
- Hostname format: `db.PROJECT-REF.supabase.co`
- Port: 5432 or 6543

**Problem in WSL:**
- WSL may not have IPv6 properly configured
- DNS resolution fails: "could not translate host name to address"
- Connection attempts timeout

**Error example:**
```
❌ ERROR: could not translate host name "dkvyhbqmeumanhnhxmxf.supabase.co" to address: Name or service not known
```

---

## The Solution: Session Pooler

### What is Session Pooler?

**Connection pooling service** provided by Supabase:
- **IPv4-compatible** hostname
- Manages connection lifecycle
- Reduces connection overhead
- Required for free tier when IPv6 unavailable

### Correct Configuration

**❌ WRONG (Direct Connection - IPv6):**
```bash
DB_HOST=db.dkvyhbqmeumanhnhxmxf.supabase.co
DB_PORT=5432 or 6543
DB_USER=postgres
```

**✅ CORRECT (Session Pooler - IPv4):**
```bash
DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_PORT=5432
DB_USER=postgres.dkvyhbqmeumanhnhxmxf
```

**Key differences:**
1. Host is AWS pooler, not direct Supabase host
2. User includes project reference: `postgres.PROJECT-REF`
3. Port is 5432 (standard PostgreSQL)

---

## Project-Specific Details

### ACAD-GIS Supabase Project
```
Project ID:       dkvyhbqmeumanhnhxmxf
Region:           us-east-2 (Ohio)
Created:          October 2024
Tier:             Free (500MB storage, auto-pause after 7 days inactivity)
```

### Connection Parameters
```bash
# Session Pooler (IPv4 - USE THIS)
Host:     aws-1-us-east-2.pooler.supabase.com
Port:     5432
Database: postgres
User:     postgres.dkvyhbqmeumanhnhxmxf
Password: <your-password>

# Full connection string
postgresql://postgres.dkvyhbqmeumanhnhxmxf:<your-password>@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

---

## Common Mistakes & Solutions

### Mistake 1: Wrong Project ID

**Symptom:**
```
FATAL: Tenant or user not found
```

**Common typos:**
- `dkwyhbqneumarhvhwmxf` (letters jumbled)
- `dkvyhbqmeumanhnhxmxf` (correct)

**Solution:**
Verify project ID in Supabase dashboard URL:
```
https://supabase.com/dashboard/project/dkvyhbqmeumanhnhxmxf
                                      ^^^^^^^^^^^^^^^^^^^^^
```

### Mistake 2: Wrong Region

**Symptom:**
```
FATAL: Tenant or user not found
```

**Wrong regions tried:**
- `aws-0-us-west-1.pooler.supabase.com` ❌
- `aws-1-us-west-2.pooler.supabase.com` ❌

**Correct region:**
- `aws-1-us-east-2.pooler.supabase.com` ✅

**How to verify:**
Check Supabase dashboard → Project Settings → Database → Connection string

### Mistake 3: Wrong Password

**Symptom:**
```
FATAL: password authentication failed for user "postgres"
```

**Causes:**
1. Password was reset in dashboard
2. Using password from wrong project
3. Typo in password

**Solution:**
Use the password from your working setup (replace `<your-password>` accordingly).

**If forgotten:**
1. Supabase Dashboard → Project Settings → Database
2. Scroll to "Reset your database password"
3. Generate new password
4. Update `.env` file

### Mistake 4: Wrong Port

**Pooler modes:**
- **Transaction mode:** Port 6543
- **Session mode:** Port 5432

**For ACAD-GIS:** Use port **5432** (Session mode)

---

## Environment Configuration

### .env File Template

**Location:** `backend/.env`
```bash
# ============================================
# Database Configuration
# ============================================
# CRITICAL: Use Session Pooler for IPv4 compatibility

# Connection Parameters
DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_NAME=postgres
DB_USER=postgres.dkvyhbqmeumanhnhxmxf
DB_PASSWORD=<your-password>
DB_PORT=5432

# Full Connection String
DATABASE_URL=postgresql://postgres.dkvyhbqmeumanhnhxmxf:<your-password>@aws-1-us-east-2.pooler.supabase.com:5432/postgres

# ============================================
# Supabase API Configuration
# ============================================
SUPABASE_URL=https://dkvyhbqmeumanhnhxmxf.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRrdnloYnFtZXVtYW5oaG5oeG14ZiIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNzI3ODA3NjE1LCJleHAiOjIwNDMzODM2MTV9.XMigueKdslJy_kEtJ4Ot67G0EqFkmqnMZP_o0oNj0Wo
```

**Security notes:**
- This file is in `.gitignore` - never committed
- Password is visible in this doc because it's for your reference
- In production, use environment variables or secret management

---

## Testing Connection

### Method 1: Python Script
```bash
cd ~/projects/acad-gis
source venv/bin/activate

python3 << 'EOF'
import psycopg2
import os

# Exact working configuration
config = {
    'host': 'aws-1-us-east-2.pooler.supabase.com',
    'database': 'postgres',
    'user': 'postgres.dkvyhbqmeumanhnhxmxf',
    'password': os.getenv('DB_PASSWORD'),
    'port': '5432'
}

try:
    conn = psycopg2.connect(**config)
    print("✅ SUCCESS: Connected to database!")
    
    # Test query
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM projects;")
    count = cur.fetchone()[0]
    print(f"📊 Found {count} projects in database")
    
    # Check tables
    cur.execute("""
        SELECT count(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    tables = cur.fetchone()[0]
    print(f"📋 Database has {tables} tables")
    
    conn.close()
    print("✅ Connection test complete!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
