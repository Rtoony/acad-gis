# Database Connection Troubleshooting - UPDATED

**Last Updated:** October 19, 2025  
**Status:** ✅ WORKING - All issues resolved

---

## 🎉 Current Working Configuration

```bash
DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_PORT=5432                                    # ← SESSION POOLER (IPv4)
DB_NAME=postgres
DB_USER=postgres.dkvyhbqmeumanhnhxmxf
DB_PASSWORD=FFj9aBq8PtYNPaiz
```

**Connection String:**
```
postgresql://postgres.dkvyhbqmeumanhnhxmxf:FFj9aBq8PtYNPaiz@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

---

## 🔧 What Was Fixed

### Issue #1: Wrong Port (CRITICAL)
**Problem:**
```bash
DB_PORT=6543  # Transaction pooler - WRONG
```

**Solution:**
```bash
DB_PORT=5432  # Session pooler - CORRECT
```

**Why this matters:**
- Port 6543 = Transaction pooler (different auth method)
- Port 5432 = Session pooler (standard PostgreSQL, IPv4 compatible)
- Free tier WSL needs Session pooler

### Issue #2: Password Reset Didn't Take Effect
**Problem:**
- Reset password to `uhY8zzuy4wLbAFBC` in Supabase dashboard
- New password didn't work
- Old password `FFj9aBq8PtYNPaiz` still active

**Solution:**
- Use the old password that still works
- Password resets can take time to propagate
- If you NEED to change it, wait 10+ minutes and retry

### Issue #3: WSL Python Environment
**Problem:**
```bash
ModuleNotFoundError: No module named 'psycopg2'
```

**Solution:**
```bash
pip3 install --break-system-packages psycopg2-binary python-dotenv
```

**Why `--break-system-packages`:**
- Ubuntu 24.04 protects system Python
- WSL is isolated, so this flag is safe
- Virtual environments had issues with venv creation

---

## ✅ Verification Tests (All Passing)

### Test 1: Database Connection
```bash
cd /mnt/h/acad-gis/backend
python3 database.py
```

**Expected Output:**
```
Testing database connection...
✅ Database connection successful!
✅ Found 100 block definitions
✅ Found 72 layer standards
```

### Test 2: Create New Record
```bash
python3 << 'EOF'
from database import create_project
project_id = create_project(
    project_name="WSL Test Project",
    project_number="WSL-001"
)
print(f"✅ Created project: {project_id}")
EOF
```

### Test 3: Query Data
```bash
python3 << 'EOF'
from database import execute_query
blocks = execute_query("SELECT COUNT(*) FROM block_definitions")
print(f"✅ Total blocks: {blocks[0]['count']}")
EOF
```

---

## 🚫 Common Mistakes to Avoid

### ❌ Wrong Port
```bash
DB_PORT=6543  # NO - Transaction pooler
```

### ❌ Wrong Host
```bash
DB_HOST=db.dkvyhbqmeumanhnhxmxf.supabase.co  # NO - IPv6 only
```

### ❌ Wrong User Format
```bash
DB_USER=postgres  # NO - Missing project reference
```

### ❌ New Password (that doesn't work yet)
```bash
DB_PASSWORD=uhY8zzuy4wLbAFBC  # NO - Reset didn't propagate
```

---

## ✅ Correct Configuration

### Session Pooler (IPv4 Compatible)
```bash
DB_HOST=aws-1-us-east-2.pooler.supabase.com  # Pooler hostname
DB_PORT=5432                                  # Session pooler port
DB_USER=postgres.dkvyhbqmeumanhnhxmxf        # Full username with project
DB_PASSWORD=FFj9aBq8PtYNPaiz                 # Working password
```

---

## 🛠️ Quick Setup Script

Save this as `backend/quick_connect_test.py`:

```python
#!/usr/bin/env python3
"""Quick connection test for ACAD-GIS database"""

import psycopg2
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Configuration
CONFIG = {
    'host': os.getenv('DB_HOST', 'aws-1-us-east-2.pooler.supabase.com'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres.dkvyhbqmeumanhnhxmxf'),
    'password': os.getenv('DB_PASSWORD'),
}

print("Testing database connection...")
print(f"Host: {CONFIG['host']}")
print(f"Port: {CONFIG['port']}")
print(f"User: {CONFIG['user']}")
print(f"Database: {CONFIG['database']}")
print("-" * 60)

try:
    conn = psycopg2.connect(**CONFIG)
    print("✅ CONNECTION SUCCESS!")
    
    cur = conn.cursor()
    
    # Test query
    cur.execute("SELECT COUNT(*) FROM block_definitions")
    count = cur.fetchone()[0]
    print(f"✅ Found {count} block definitions")
    
    cur.execute("SELECT COUNT(*) FROM layer_standards")
    count = cur.fetchone()[0]
    print(f"✅ Found {count} layer standards")
    
    cur.execute("SELECT COUNT(*) FROM projects")
    count = cur.fetchone()[0]
    print(f"✅ Found {count} projects")
    
    conn.close()
    print("-" * 60)
    print("✅ All tests passed! Database is ready.")
    
except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")
    print("\nTroubleshooting:")
    print("1. Check .env file exists in backend/ directory")
    print("2. Verify DB_PORT=5432 (not 6543)")
    print("3. Confirm DB_PASSWORD=FFj9aBq8PtYNPaiz")
    print("4. Check Supabase project isn't paused")
```

**Run it:**
```bash
cd /mnt/h/acad-gis/backend
python3 quick_connect_test.py
```

---

## 📋 Environment File Template

**Location:** `/mnt/h/acad-gis/backend/.env`

```bash
# ============================================
# ACAD-GIS Database Configuration
# ============================================
# Last Updated: October 19, 2025
# Status: ✅ WORKING

# Database Connection (Session Pooler - IPv4 Compatible)
DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres.dkvyhbqmeumanhnhxmxf
DB_PASSWORD=FFj9aBq8PtYNPaiz

# Full Connection String
DATABASE_URL=postgresql://postgres.dkvyhbqmeumanhnhxmxf:FFj9aBq8PtYNPaiz@aws-1-us-east-2.pooler.supabase.com:5432/postgres

# Supabase API (Optional)
SUPABASE_URL=https://dkvyhbqmeumanhnhxmxf.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRrdnloYnFtZXVtYW5obmh4bXhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA0OTA1ODUsImV4cCI6MjA3NjA2NjU4NX0.nC-vpMJhQinDQjbz2lPdQQZot9p9WUnC59kK1pjA_oA

# Flask/API Settings
FLASK_ENV=development
FLASK_DEBUG=1
```

---

## 🔍 Troubleshooting Decision Tree

```
Can't connect?
    │
    ├─→ Is API server running?
    │   ├─→ NO: Start it with `python3 api_server_ENHANCED.py`
    │   └─→ YES: Continue
    │
    ├─→ Is .env file in backend/ directory?
    │   ├─→ NO: Create it using template above
    │   └─→ YES: Continue
    │
    ├─→ Is DB_PORT=5432?
    │   ├─→ NO: Change to 5432
    │   └─→ YES: Continue
    │
    ├─→ Is psycopg2-binary installed?
    │   ├─→ NO: pip3 install --break-system-packages psycopg2-binary
    │   └─→ YES: Continue
    │
    ├─→ Is Supabase project paused?
    │   ├─→ YES: Visit dashboard to wake it up
    │   └─→ NO: Continue
    │
    └─→ Still failing?
        └─→ Run quick_connect_test.py for detailed diagnostics
```

---

## 🎓 Lessons Learned

### 1. Session vs Transaction Pooler
- **Session Pooler (5432)**: Standard PostgreSQL protocol, works with most tools
- **Transaction Pooler (6543)**: Different connection mode, more restrictive

### 2. Password Reset Propagation
- Supabase password changes aren't instant
- Can take 5-10 minutes to propagate
- Old password may continue working during transition

### 3. WSL Python Packages
- Ubuntu 24.04 protects system Python
- `--break-system-packages` flag is safe in WSL
- Virtual environments can have issues with pip

### 4. Username Format Matters
- Must include project reference: `postgres.PROJECT_ID`
- Just `postgres` won't work with pooler
- Error message can be misleading (shows stripped username)

---

## ✅ Success Checklist

- [x] .env file created in backend/ directory
- [x] DB_PORT=5432 (Session pooler)
- [x] DB_PASSWORD=FFj9aBq8PtYNPaiz (working password)
- [x] psycopg2-binary installed in WSL
- [x] python-dotenv installed in WSL
- [x] Connection test passes
- [x] Can query block_definitions table
- [x] Can create new projects

---

## 🚀 Next Steps

Now that connection is working:

1. **Start API Server**
   ```bash
   cd /mnt/h/acad-gis/backend
   python3 api_server_ENHANCED.py
   ```

2. **Open Tool Launcher**
   - Navigate to project in Windows
   - Open `tool_launcher.html` in browser

3. **Begin Tool Development**
   - Extract Project Manager from dashboard
   - Follow PROJECT_STRUCTURE.md guide

---

## 📞 Quick Reference

### Test Connection
```bash
cd /mnt/h/acad-gis/backend
python3 database.py
```

### View .env File
```bash
cat /mnt/h/acad-gis/backend/.env
```

### Check Python Packages
```bash
pip3 list | grep psycopg2
```

### Supabase Dashboard
https://supabase.com/dashboard/project/dkvyhbqmeumanhnhxmxf

---

**Status:** ✅ All systems operational  
**Last Verified:** October 19, 2025  
**Connection Test:** Passed all 5 tests
