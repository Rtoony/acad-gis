# WSL Development Environment - COMPLETE SETUP

**Created:** October 19, 2025  
**Status:** ✅ FULLY OPERATIONAL  
**System:** Windows 11 + WSL Ubuntu 24.04

---

## 🎉 Setup Complete!

Your ACAD-GIS development environment is fully configured and tested:

✅ WSL Ubuntu 24.04 installed  
✅ Windows Terminal configured  
✅ Git configured with GitHub SSH  
✅ Python 3.12 with required packages  
✅ Database connection working  
✅ All tests passing  

---

## 📍 System Configuration

### File Locations

**Windows Side:**
```
H:\acad-gis\                           # Main project (Windows drive)
├── backend\                           # Python API server
│   ├── .env                          # Database credentials
│   ├── api_server.py        # FastAPI server
│   └── database.py                   # Database functions
├── frontend\
│   ├── tools\                        # Individual mini-tools
│   └── shared\                       # CSS/JS shared resources
└── docs\                             # Documentation
```

**WSL Side (Access Windows files):**
```
/mnt/h/acad-gis/                      # Same project, accessed from WSL
```

**WSL Native (Faster for pure Linux work):**
```
~/projects/                           # Could also work here
```

### Recommended: Work from Windows H: Drive
```bash
# In WSL, navigate to Windows drive
cd /mnt/h/acad-gis
```

**Why:**
- Files visible in both Windows and WSL
- Can edit with Windows editors
- Git works from both sides
- Easy to access from File Explorer

---

## 🔧 Installed Software

### WSL Environment
```
Distribution:  Ubuntu 24.04 LTS
Kernel:        WSL 2
Python:        3.12.x
Git:           2.x
Terminal:      Windows Terminal
```

### Python Packages (Installed Globally)
```bash
# Check installed packages
pip3 list

# Key packages:
psycopg2-binary==2.9.11    # PostgreSQL adapter
python-dotenv==1.1.1       # Environment variables
fastapi==0.119.0           # Web framework (if needed)
uvicorn==0.38.0            # ASGI server (if needed)
```

**Installation method used:**
```bash
pip3 install --break-system-packages psycopg2-binary python-dotenv
```

**Note:** Using `--break-system-packages` is safe in WSL since it's isolated.

---

## 🗄️ Database Configuration

### Supabase Connection Details

**Project:**
```
Name:          CADGIS
Project ID:    dkvyhbqmeumanhnhxmxf
Region:        us-east-2 (Ohio)
Database:      PostgreSQL 15 with PostGIS + pgvector
```

**Working Connection (Session Pooler):**
```
Host:     aws-1-us-east-2.pooler.supabase.com
Port:     5432                                    ← CRITICAL
Database: postgres
User:     postgres.dkvyhbqmeumanhnhxmxf          ← Includes project ID
Password: <your-password>                       ← Set this to your current Supabase password
```

**Connection String:**
```
postgresql://postgres.dkvyhbqmeumanhnhxmxf:<your-password>@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

### Environment File

**Location:** `H:\acad-gis\backend\.env`  
**WSL Path:** `/mnt/h/acad-gis/backend/.env`

**Contents:**
```bash
DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres.dkvyhbqmeumanhnhxmxf
DB_PASSWORD=<your-password>

DATABASE_URL=postgresql://postgres.dkvyhbqmeumanhnhxmxf:<your-password>@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

---

## ✅ Verification Tests (All Passed)

### Test 1: Database Connection
```bash
cd /mnt/h/acad-gis/backend
python3 database.py
```

**Result:**
```
✅ Database connection successful!
✅ Found 100 block definitions
✅ Found 72 layer standards
```

### Test 2: All Tables Present
```bash
python3 << 'EOF'
from database import execute_query
tables = ['block_definitions', 'layer_standards', 'projects', 'drawings']
for table in tables:
    result = execute_query(f"SELECT COUNT(*) as count FROM {table}")
    print(f"✅ {table}: {result[0]['count']} records")
EOF
```

**Result:**
```
✅ block_definitions: 100 records
✅ layer_standards: 72 records
✅ projects: 1+ records
✅ drawings: 1+ records
```

### Test 3: Create New Record
```bash
python3 << 'EOF'
from database import create_project
project_id = create_project(
    project_name="WSL Connection Test",
    project_number="WSL-001"
)
print(f"✅ Created project: {project_id}")
EOF
```

**Result:**
```
✅ Created project: [UUID]
```

---

## 🎯 Daily Workflow

### Opening WSL
1. Open **Windows Terminal**
2. New tab auto-opens WSL Ubuntu
3. You'll see: `josh_patheal@DESKTOP-F4AKB2B:~$`

### Starting Work
```bash
# Navigate to project
cd /mnt/h/acad-gis/backend

# Verify connection
python3 database.py

# Start API server
python3 api_server.py
```

**API server output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Testing API
**From WSL:**
```bash
curl http://localhost:8000/api/health
```

**From Windows browser:**
```
http://localhost:8000/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-10-19T..."
}
```

---

## 🐙 Git Configuration

### Git Identity
```bash
git config --global user.name "Josh Patheal"
git config --global user.email "joshpatheal@gmail.com"
git config --global init.defaultBranch main
```

**Verify:**
```bash
git config --global --list
```

### GitHub SSH Setup

**SSH Key Location:**
```
~/.ssh/id_ed25519      # Private key (never share)
~/.ssh/id_ed25519.pub  # Public key (added to GitHub)
```

**Test SSH connection:**
```bash
ssh -T git@github.com
```

**Expected output:**
```
Hi Rtoony! You've successfully authenticated, but GitHub does not provide shell access.
```

### Repository

**URL:** https://github.com/Rtoony/acad-gis  
**Clone command:** `git clone git@github.com:Rtoony/acad-gis.git`

**Current location:** `H:\acad-gis\` (already cloned)

---

## 🚀 Running the Project

### Start API Server (WSL Terminal)
```bash
cd /mnt/h/acad-gis/backend
python3 api_server.py
```

**Leave this running** - don't close the terminal.

### Open Frontend (Windows)
1. Navigate to `H:\acad-gis\` in File Explorer
2. Double-click `tool_launcher.html`
3. Browser opens with tool dashboard
4. API status should show **green "Connected"**

### Verify Everything Works
- Tool Launcher loads
- API status indicator is green
- Statistics display (projects, drawings, symbols)
- Can click on tool cards

---

## 📦 Package Management

### Installing Python Packages

**Method used:**
```bash
pip3 install --break-system-packages PACKAGE_NAME
```

**Why `--break-system-packages`:**
- Ubuntu 24.04 protects system Python
- WSL is isolated environment (safe to use)
- Virtual environments had setup issues

**Currently installed:**
```bash
pip3 list
```

**To add more packages:**
```bash
pip3 install --break-system-packages fastapi uvicorn
```

---

## 🛠️ Useful Commands

### File Navigation
```bash
# Go to project
cd /mnt/h/acad-gis

# List files
ls -la

# Open current directory in Windows Explorer
explorer.exe .

# Open file in VS Code
code filename.py
```

### Python
```bash
# Run Python script
python3 script.py

# Python interactive shell
python3

# Check Python version
python3 --version
```

### Git
```bash
# Check status
git status

# View recent commits
git log --oneline

# Push changes
git add .
git commit -m "Your message"
git push
```

### Database Testing
```bash
# Quick connection test
python3 database.py

# Run SQL query
python3 -c "from database import execute_query; print(execute_query('SELECT COUNT(*) FROM projects'))"
```

---

## 🐛 Common Issues & Solutions

### "command not found: python"
**Solution:** Use `python3` instead of `python`

### "Module not found: psycopg2"
**Solution:**
```bash
pip3 install --break-system-packages psycopg2-binary python-dotenv
```

### "Permission denied" when accessing files
**Solution:** Work from `/mnt/h/acad-gis` (Windows side)

### "Connection refused" from database
**Solutions:**
1. Check `.env` file exists
2. Verify `DB_PORT=5432` (not 6543)
3. Confirm Supabase project isn't paused
4. Run `python3 database.py` to test

### Git asks for password
**Solution:** Use SSH instead of HTTPS
```bash
git remote set-url origin git@github.com:Rtoony/acad-gis.git
```

---

## 📊 Project Statistics

**As of October 19, 2025:**

```
Database Tables:       22 (all verified)
Block Definitions:     100
Layer Standards:       72
Projects:              Multiple test projects
Drawings:              Multiple test drawings
```

**Connection Stats:**
- Session Pooler (IPv4): ✅ Working
- Transaction Pooler: ❌ Don't use
- Direct Connection: ❌ IPv6 not configured

---

## 🎓 Tips & Best Practices

### Terminal Workflow
1. Keep API server running in one terminal tab
2. Use second tab for git commands
3. Use third tab for testing/database queries

### File Editing
- Edit files in Windows using your preferred editor
- Changes immediately visible in WSL
- Git works from either side

### Git Commits
- Commit frequently (end of day minimum)
- Write descriptive commit messages
- Push to GitHub daily

### Database
- Always use Session Pooler (port 5432)
- Don't commit `.env` file to Git
- Test connection after system restart

---

## 📚 Next Steps

1. ✅ WSL configured
2. ✅ Database connected
3. ✅ Git configured
4. ✅ All tests passing
5. 🎯 **Next: Begin tool development**

**Follow:** PROJECT_STRUCTURE.md for development roadmap

---

## 🏆 Success Criteria

- [x] WSL Ubuntu installed and updated
- [x] Windows Terminal configured
- [x] Git identity configured
- [x] GitHub SSH authentication working
- [x] Python packages installed
- [x] Database connection working
- [x] Can create/query database records
- [x] API server starts successfully
- [x] Tool Launcher displays correctly
- [x] Git push/pull working

---

## 📞 Quick Reference

### Paths
```bash
Project:   /mnt/h/acad-gis
Backend:   /mnt/h/acad-gis/backend
Frontend:  /mnt/h/acad-gis/frontend
```

### Commands
```bash
# Start work
cd /mnt/h/acad-gis/backend
python3 database.py                    # Test connection
python3 api_server.py         # Start API

# Git
git status                             # Check changes
git pull                               # Get updates
git push                               # Send commits
```

### URLs
```
API Health:     http://localhost:8000/api/health
API Docs:       http://localhost:8000/docs
Supabase:       https://supabase.com/dashboard/project/dkvyhbqmeumanhnhxmxf
GitHub:         https://github.com/Rtoony/acad-gis
```

---

**Environment Status:** ✅ FULLY OPERATIONAL  
**Last Verified:** October 19, 2025  
**All Systems:** GO for development!
