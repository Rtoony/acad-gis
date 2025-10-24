# ACAD=GIS Setup Guide

**Last Updated**: October 17, 2025  
**Status**: Tested and Working Configuration  
**Schema Version**: 2.0

This guide documents the exact configuration that works for your Supabase free tier setup.

---

## Prerequisites

### Required Software
- [x] Python 3.13 (installed)
- [x] pip (Python package manager)
- [ ] CAD Software (AutoCAD, DraftSight, LibreCAD, or similar)
- [x] Git (for version control)
- [x] Text editor (VS Code recommended)

### Required Accounts
- [x] Supabase account (free tier)
- [x] OpenAI API account (for embeddings)

---

## Step 1: Supabase Configuration

### Your Project Details
- **Project Name**: CADGIS
- **Project Reference**: `dkvyhbqmeumanhnhxmxf`
- **Region**: AWS US East 2
- **Database**: PostgreSQL 15 with PostGIS + pgvector

### Important: Connection Method

⚠️ **Your project is IPv6-only for direct connections**. You MUST use the Session Pooler for IPv4 compatibility.

#### Correct Connection String
```
Host: aws-1-us-east-2.pooler.supabase.com
Port: 5432
Method: Session pooler
```

#### ❌ Don't Use (IPv6 only)
```
Host: db.dkvyhbqmeumanhnhxmxf.supabase.co
Port: 5432
```

### Get Your Connection Details

1. Go to: https://supabase.com/dashboard/project/dkvyhbqmeumanhnhxmxf
2. Click **Project Settings** (gear icon) → **Database**
3. Scroll to **Connection string**
4. Select **URI** format
5. Change **Method** dropdown to: **Session pooler**
6. Copy the connection details

---

## Step 2: Environment Variables

### Create `.env` File

In your project directory (`C:\Users\Josh\Desktop\ACAD_GIS\Supporting Documents`), create a file named `.env`:

```bash
# .env file - SESSION POOLER (IPv4 Compatible)
DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres.dkvyhbqmeumanhnhxmxf
DB_PASSWORD=<your-password>

OPENAI_API_KEY=sk-proj-...
```

### ⚠️ Security Notes
- Never commit `.env` to Git
- Keep backups in secure location
- Rotate passwords periodically
- Use environment variables in production

### Verify `.gitignore` Exists

Ensure `.gitignore` contains:
```
# Environment variables (contains secrets!)
.env

# Python
__pycache__/
*.py[cod]
venv/

# Database
*.db

# Temp files
*.dxf.bak
/tmp/
*.tmp
```

---

## Step 3: Python Environment

### Install Required Packages

```bash
pip install psycopg2-binary python-dotenv ezdxf openai
```

### Package Versions (Known Working)
```
psycopg2-binary==2.9.9
python-dotenv==1.0.0
ezdxf==1.3.0
openai==1.3.0
```

### Create `requirements.txt` (Optional)
```bash
pip freeze > requirements.txt
```

---

## Step 4: Database Configuration

### Critical: SSL Settings in `database.py`

Your `database.py` MUST include these SSL settings:

```python
# Database configuration - loads from .env file
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'sslmode': 'prefer',  # Critical for Supabase
    'connect_timeout': 10,
    'keepalives': 1,
    'keepalives_idle': 30,
    'keepalives_interval': 10,
    'keepalives_count': 5
}
```

### Why These Settings Matter
- `sslmode: 'prefer'` - More forgiving than 'require', prevents SSL drops
- `keepalives` - Prevents connection timeouts with pooler
- `connect_timeout: 10` - Reasonable timeout for remote database

---

## Step 5: Verify Setup

### Test 1: Environment Variables
```bash
python test_env.py
```

**Expected Output**:
```
✅ Connection successful!
✅ Found 70 symbols in database
✅ Found 72 layer standards
```

### Test 2: Full Database Audit
```bash
python check_database_status.py
```

**Expected Output**:
```
============================================================
DATABASE AUDIT RESULTS
============================================================
CORE TABLES (17 expected):
------------------------------------------------------------
✅ block_definitions              | Count: 70
✅ block_attributes               | Count: 0
✅ block_attribute_values         | Count: 0
✅ block_inserts                  | Count: 0
✅ layer_standards                | Count: 72
✅ layers                         | Count: 6
✅ projects                       | Count: 1
✅ drawings                       | Count: 1
... (17 core tables)

CAD STANDARDS TABLES (5 expected):
------------------------------------------------------------
✅ linetype_standards             | Count: 8
✅ text_styles                    | Count: 6
✅ dimension_styles               | Count: 5
✅ hatch_patterns                 | Count: 7
✅ detail_standards               | Count: 7
============================================================
TOTAL TABLES: 22/22
============================================================
```

### Test 3: Verify CAD Standards
```bash
python verify_data_counts.py
```

**Expected Output**:
```
DATA COUNT VERIFICATION:
======================================================================
✅ block_definitions         | Expected:  70 | Actual:  70
✅ layer_standards           | Expected:  72 | Actual:  72
✅ projects                  | Expected:   1 | Actual:   1
✅ drawings                  | Expected:   1 | Actual:   1
ℹ️  color_standards           | Expected: 9+  | Actual:   9
✅ linetype_standards        | Expected:   8 | Actual:   8
✅ text_styles               | Expected:   6 | Actual:   6
✅ dimension_styles          | Expected:   5 | Actual:   5
✅ hatch_patterns            | Expected:   7 | Actual:   7
✅ detail_standards          | Expected:   7 | Actual:   7
======================================================================
```

### Test 4: Block Enhancements
```bash
python check_block_enhancements.py
```

**Expected Output**:
```
BLOCK_DEFINITIONS COLUMNS:
------------------------------------------------------------
... (standard columns)
NEW is_title_block            | boolean              | false
NEW is_detail                 | boolean              | false
NEW title_block_size          | character varying    | NULL
NEW detail_category           | character varying    | NULL

ENHANCEMENT STATUS:
------------------------------------------------------------
✅ is_title_block
✅ is_detail
✅ title_block_size
✅ detail_category
```

---

## Step 6: First Project & Drawing

### Create a Project
```bash
python -c "from database import create_project; pid = create_project('My First Project', 'PROJ-001', 'Client Name', 'Project description'); print(f'Project ID: {pid}')"
```

**Save the Project ID** - you'll need it for the next step.

### Create a Test Drawing
```bash
python create_test_drawing.py --project-id <paste-project-id-here>
```

**Expected Output**:
```
✅ Drawing ID: <some-uuid>
File: test_drawing.dxf
```

### Open the Drawing
```bash
# Windows
start test_drawing.dxf

# Or open manually in your CAD software
```

You should see:
- Property boundary (gray)
- Water main line (gray)
- Sewer main line (gray)
- Building footprint (gray)
- "TEST SITE PLAN" text

---

## Step 7: Test Core Functionality

### Export Drawing
```bash
python export_dxf.py --drawing-id <drawing-id> --output exported.dxf
```

### Import Real DXF
```bash
python import_dxf.py --file "path\to\your\drawing.dxf" --project-id <project-id> --name "My Drawing" --type "TOPO SURVEY"
```

### Sync Workflow
```bash
python sync_drawing.py --drawing-id <drawing-id>
```

This will:
1. Export to temp file
2. Open in CAD software
3. Wait for you to edit
4. Press Enter when done
5. Re-import changes

---

## Step 8: Verify CAD Standards (Optional)

### Check Available Linetypes
```bash
python -c "from database import execute_query; print('\n'.join([r['linetype_name'] for r in execute_query('SELECT linetype_name FROM linetype_standards ORDER BY linetype_name')]))"
```

**Expected Output**:
```
CENTER
CONTINUOUS
DASHED
DOT
FENCELINE
GAS_LINE
HIDDEN
PHANTOM
```

### Check Text Styles
```bash
python -c "from database import execute_query; print('\n'.join([r['style_name'] for r in execute_query('SELECT style_name FROM text_styles ORDER BY style_name')]))"
```

**Expected Output**:
```
DIMENSIONS
LABELS
NOTES
SMALL
STANDARD
TITLES
```

### Check Construction Details
```bash
python -c "from database import execute_query; print('\n'.join([f\"{r['detail_number']}: {r['detail_title']}\" for r in execute_query('SELECT detail_number, detail_title FROM detail_standards ORDER BY detail_number')]))"
```

**Expected Output**:
```
GD-1: Standard Curb and Gutter Section
GD-2: Grading Transition Detail
LD-1: Tree Planting Detail
SD-1: Standard Storm Drain Manhole
SD-2: Storm Drain Inlet
SD-3: Storm Drain Connection
WD-1: Water Service Connection
```

---

## Common Issues & Solutions

For detailed troubleshooting, see **TROUBLESHOOTING.md**.

### Quick Fixes

**"SSL connection has been closed"**
→ Verify `database.py` has SSL settings from Step 4

**"DNS resolution failed"**
→ Use `aws-1-us-east-2.pooler.supabase.com`, not the direct hostname

**"Connection timeout"**
→ Check if Supabase project is paused in dashboard

**"Module not found"**
→ `pip install psycopg2-binary python-dotenv ezdxf openai`

**"AttributeError: 'Text' object has no attribute..."**
→ ezdxf API changed; see TROUBLESHOOTING.md for fixes

**"Table not found"**
→ Run full audit: `python check_database_status.py`

---

## Maintenance

### Keep Supabase Project Active

Free tier projects pause after 7 days of inactivity.

**Options**:
1. Visit dashboard weekly
2. Run a daily cron job: `python test_env.py`
3. Upgrade to paid tier ($25/mo)

### Backup Database

```bash
# From Supabase dashboard
# Project Settings → Database → Backups
# Daily automatic backups on free tier
```

### Monitor Usage

Check Supabase dashboard:
- Database size: Max 500MB on free tier
- API requests: Max 50,000/month
- Bandwidth: Max 5GB/month

### Rotate Passwords

If you need to change passwords:
1. Update in Supabase dashboard
2. Update `.env` file
3. Test connection: `python test_env.py`

---

## Next Steps

1. ✅ Setup complete
2. ✅ All 22 tables verified
3. ✅ CAD standards populated
4. 📋 Review `TESTING_CHECKLIST.md`
5. 📊 Check `PROJECT_STATUS.md`
6. 🚀 Start importing real DXF files
7. 🤖 Generate embeddings when ready

---

## Quick Reference

### Project IDs
- **Test Project**: `5f264826-a572-4291-96e1-bdb890b1808b`
- **Test Drawing**: `680c5373-8e73-43a2-a808-d34820e5d597`

### Key Files
- **Config**: `.env`
- **Database**: `database.py`
- **Import**: `import_dxf.py`
- **Export**: `export_dxf.py`
- **Sync**: `sync_drawing.py`
- **Test**: `test_env.py`
- **Audit**: `check_database_status.py`

### Database Stats (Current)
- **Schema Version**: 2.0
- **Total Tables**: 22 (17 core + 5 CAD standards)
- **Symbols**: 70
- **Layers**: 72
- **Colors**: 9
- **Linetypes**: 8
- **Text Styles**: 6
- **Dimension Styles**: 5
- **Hatch Patterns**: 7
- **Construction Details**: 7
- **Projects**: 1
- **Drawings**: 1

### Connection String
```
postgresql://postgres.dkvyhbqmeumanhnhxmxf:[PASSWORD]@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

---

## Schema Version Information

**Current Version**: 2.0

**What's New in v2.0**:
- ✅ 5 CAD standards tables added and populated
- ✅ Block enhancements for title blocks and details
- ✅ 33 standard CAD elements (linetypes, styles, patterns, details)
- ✅ Full AI-ready infrastructure

**Upgrade from v1.0**:
- No migration needed - all new tables
- Existing data preserved
- New features immediately available

---

**Status**: System operational and ready for real-world testing. All 22 tables verified deployed and functional. CAD standards library fully populated.