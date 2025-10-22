# ACAD-GIS Development Environment

**Created:** October 19, 2025  
**Last Updated:** October 19, 2025  
**Status:** ✅ Fully Configured and Working

---

## Current Configuration

### System Information
```
OS:              Windows 11
WSL Version:     2
Distribution:    Ubuntu 24.04
Python Version:  3.12
Terminal:        Windows Terminal
Editor:          VS Code with WSL Remote extension
Shell:           bash
```

### User Details
```
WSL Username:    josh_patheal
GitHub Username: Rtoony
GitHub Email:    joshpatheal@gmail.com
Project Name:    acad-gis
```

---

## Project Structure
```
~/projects/acad-gis/                    # WSL: Main project directory
├── .git/                               # Git repository metadata
├── .gitignore                          # Files to ignore in Git
├── README.md                           # Project overview
├── requirements.txt                    # Python dependencies
│
├── venv/                               # Python virtual environment (NOT in Git)
│   ├── bin/                            # Executables (python, pip, uvicorn)
│   ├── lib/                            # Installed packages
│   └── ...
│
├── backend/                            # API server and database logic
│   ├── .env                            # Environment variables (NOT in Git)
│   ├── .env.example                    # Example env file (IS in Git)
│   ├── api_server.py          # FastAPI server
│   ├── database.py                     # Database connection helpers
│   ├── import_dxf_georef.py            # DXF import script
│   └── requirements.txt                # Backend-specific dependencies (legacy)
│
├── frontend/                           # Web interface components
│   ├── tools/                          # Individual mini-tools (to be created)
│   │   ├── project_manager.html
│   │   ├── drawing_importer.html
│   │   ├── map_viewer.html
│   │   ├── drawing_browser.html
│   │   └── symbol_library.html
│   │
│   └── shared/                         # Shared assets across tools
│       ├── styles.css                  # Mission Control theme
│       ├── api.js                      # API wrapper functions
│       └── components.js               # Reusable React components
│
├── docs/                               # Documentation
│   ├── README.md                       # Project overview
│   ├── WSL_SETUP.md                    # WSL environment setup
│   ├── DEVELOPMENT_ENVIRONMENT.md      # This file
│   ├── DATABASE_CONNECTION.md          # Supabase configuration
│   ├── GIT_WORKFLOW.md                 # Git usage guide
│   ├── PROJECT_CONTEXT.md              # Context for LLM assistance
│   ├── SETUP_GUIDE.md                  # Original setup guide
│   ├── DATABASE_SCHEMA_GUIDE.md        # Database schema
│   └── QUICK_REFERENCE.md              # Quick reference
│
├── database/                           # Database-related files
│   ├── schema.sql                      # PostgreSQL schema (to be exported)
│   └── migrations/                     # Future migrations
│
├── scripts/                            # Utility scripts
│   ├── start_api.sh                    # Start API server (to be created)
│   ├── start_launcher.sh               # Open tool launcher (to be created)
│   └── test_connection.py              # Test database connection (to be created)
│
├── tests/                              # Test files
│   └── test_api_health.py              # API health checks (to be created)
│
└── archive/                            # Archived/reference files
    └── dashboard_MISSION_CONTROL_V2.html  # Original monolithic dashboard
```

---

## Python Environment

### Virtual Environment Location
```bash
Path:     ~/projects/acad-gis/venv/
Python:   /home/josh_patheal/projects/acad-gis/venv/bin/python3
Pip:      /home/josh_patheal/projects/acad-gis/venv/bin/pip
```

### Activation
```bash
# From anywhere in the project
cd ~/projects/acad-gis
source venv/bin/activate

# Verify (prompt changes)
(venv) josh_patheal@DESKTOP-F4AKB2B:~/projects/acad-gis$

# Check Python path
which python
# Output: /home/josh_patheal/projects/acad-gis/venv/bin/python
```

### Installed Packages

**Core Dependencies:**
```
fastapi==0.119.0           # Web framework
uvicorn==0.38.0            # ASGI server
psycopg2-binary==2.9.11    # PostgreSQL adapter
python-dotenv==1.1.1       # Environment variable loader
python-multipart==0.0.20   # File upload support
pydantic==2.12.3           # Data validation
starlette==0.48.0          # ASGI toolkit
```

**View all:**
```bash
pip list
```

**Update requirements.txt:**
```bash
pip freeze > requirements.txt
```

---

## Database Configuration

### Supabase Project Details
```
Project ID:  dkvyhbqmeumanhnhxmxf
Region:      us-east-2 (Ohio)
Host:        aws-1-us-east-2.pooler.supabase.com
Port:        5432
Database:    postgres
User:        postgres.dkvyhbqmeumanhnhxmxf
```

### Connection Method

**✅ Using Session Pooler (IPv4 compatible)**

**Why Session Pooler:**
- Supabase free tier uses IPv6 for direct connections
- WSL may not have IPv6 configured
- Session pooler provides IPv4 compatibility
- More reliable in development environments

**Connection String Format:**
```
postgresql://postgres.dkvyhbqmeumanhnhxmxf:[PASSWORD]@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

### Environment Variables

**File:** `backend/.env` (NOT in Git)
```bash
# Database Configuration
DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_NAME=postgres
DB_USER=postgres.dkvyhbqmeumanhnhxmxf
DB_PASSWORD=FFj9aBq8PtYNPaiz
DB_PORT=5432

# Full connection string
DATABASE_URL=postgresql://postgres.dkvyhbqmeumanhnhxmxf:FFj9aBq8PtYNPaiz@aws-1-us-east-2.pooler.supabase.com:5432/postgres

# Supabase API settings
SUPABASE_URL=https://dkvyhbqmeumanhnhxmxf.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRrdnloYnFtZXVtYW5oaG5oeG14ZiIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNzI3ODA3NjE1LCJleHAiOjIwNDMzODM2MTV9.XMigueKdslJy_kEtJ4Ot67G0EqFkmqnMZP_o0oNj0Wo
```

**Security Note:** `.env` is in `.gitignore` - never committed to Git

---

## API Server

### Starting the Server
```bash
# Navigate to project
cd ~/projects/acad-gis

# Activate venv
source venv/bin/activate

# Start server from backend directory
cd backend
uvicorn api_server:app --reload --host 0.0.0.0 --port 5000
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['/home/josh_patheal/projects/acad-gis/backend']
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
INFO:     Started reloader process [443] using StatReload
INFO:     Started server process [445]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Server Details
```
Framework:     FastAPI
ASGI Server:   Uvicorn
Host:          0.0.0.0 (all interfaces)
Port:          5000
Reload:        Enabled (watches for file changes)
Access URLs:   http://localhost:5000
               http://127.0.0.1:5000
```

### API Endpoints

**Base URL:** `http://localhost:5000`

**Core Endpoints:**
```
GET  /                              # Root / health check
GET  /api/health                    # Health status + DB connection
GET  /api/stats                     # System statistics

GET  /api/projects                  # List all projects
POST /api/projects                  # Create project
GET  /api/projects/{project_id}     # Get project details
PUT  /api/projects/{project_id}     # Update project
DELETE /api/projects/{project_id}   # Delete project

GET  /api/drawings                  # List all drawings
POST /api/drawings                  # Create drawing
GET  /api/drawings/{drawing_id}     # Get drawing details
PUT  /api/drawings/{drawing_id}     # Update drawing
DELETE /api/drawings/{drawing_id}   # Delete drawing

POST /api/import/dxf                # Import DXF file
GET  /api/export/{drawing_id}       # Export drawing

GET  /docs                          # Interactive API docs (Swagger)
GET  /openapi.json                  # OpenAPI schema
```

### Testing Endpoints
```bash
# Health check
curl http://localhost:5000/api/health

# Get projects
curl http://localhost:5000/api/projects

# Get drawings
curl http://localhost:5000/api/drawings

# View interactive docs
# Open browser: http://localhost:5000/docs
```

---

## Git Configuration

### Repository Details
```
GitHub URL:    https://github.com/Rtoony/acad-gis
Clone URL:     git@github.com:Rtoony/acad-gis.git
Branch:        main
Remote:        origin
Visibility:    Private
```

### Git Status
```bash
# Check current status
git status

# View commit history
git log --oneline

# View remote URL
git remote -v
```

### Current Commits
```
acfddac  Initial project structure and folders
196a688  Add Python dependencies
bc42c74  Add core backend files and dashboard archive
4ef8d94  Fix: Install FastAPI dependencies instead of Flask
[latest] Fix: Configure correct Supabase connection (aws-1-us-east-2)
```

---

## VS Code Configuration

### Opening Project
```bash
cd ~/projects/acad-gis
code .
```

**Result:** VS Code opens with:
- Bottom-left: "WSL: Ubuntu" indicator
- File tree showing project structure
- Integrated terminal in WSL bash

### Recommended Extensions

**Auto-installed for WSL:**
- WSL (Microsoft)
- Remote - WSL (Microsoft)

**Recommended to install:**
- Python (Microsoft)
- Pylance (Microsoft)
- GitLens (Eric Amodio)
- Prettier (code formatter)
- EditorConfig (consistent formatting)

### Python Interpreter

**Select venv interpreter:**
1. `Ctrl+Shift+P` → "Python: Select Interpreter"
2. Choose: `./venv/bin/python`

**Verify:**
Bottom bar should show: `Python 3.12.x ('venv': venv)`

---

## Daily Workflow

### Morning Startup
```bash
# 1. Open Windows Terminal
# 2. Navigate to project
cd ~/projects/acad-gis

# 3. Activate venv
source venv/bin/activate

# 4. Pull latest changes from GitHub
git pull

# 5. Start API server (Terminal Tab 1)
cd backend
uvicorn api_server:app --reload --host 0.0.0.0 --port 5000

# 6. Open VS Code (Terminal Tab 2)
cd ~/projects/acad-gis
code .
```

### During Development
```bash
# Check what files changed
git status

# View changes in detail
git diff

# Test API endpoint
curl http://localhost:5000/api/projects
```

### End of Day
```bash
# 1. Stop API server (Ctrl+C in Terminal Tab 1)

# 2. Stage all changes
git add .

# 3. Commit with descriptive message
git commit -m "feat: Extract project manager tool from dashboard"

# 4. Push to GitHub
git push

# 5. Verify on GitHub
# Visit: https://github.com/Rtoony/acad-gis/commits/main
```

---

## Testing Database Connection

### Quick Test
```bash
cd ~/projects/acad-gis
source venv/bin/activate

python3 << 'EOF'
import psycopg2

try:
    conn = psycopg2.connect(
        host='aws-1-us-east-2.pooler.supabase.com',
        database='postgres',
        user='postgres.dkvyhbqmeumanhnhxmxf',
        password='FFj9aBq8PtYNPaiz',
        port='5432'
    )
    
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM projects;")
    count = cur.fetchone()[0]
    
    print(f"✅ Connected! Found {count} projects.")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
