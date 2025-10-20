# ACAD-GIS Project Context for LLM Assistance

**Created:** October 19, 2025  
**Purpose:** Provide complete context to LLMs (like Claude Code) when helping with development

---

## Project Overview

### What is ACAD-GIS?

**A GIS-enabled CAD drawing management system** that:
1. Imports AutoCAD DXF files into PostgreSQL/PostGIS database
2. Stores drawing geometry, blocks, layers with geographic coordinates
3. Provides web-based tools for viewing, searching, and managing drawings
4. Integrates with GIS data (parcels, roads, buildings) for context

### Why This Project Exists

**Problem:** CAD drawings are isolated files
- Hard to search across multiple drawings
- No geographic context
- Difficult to share/collaborate
- Version control is manual

**Solution:** Database-backed CAD management
- Centralized drawing storage
- Searchable geometry and metadata
- Geographic visualization on maps
- Web-based access from anywhere

---

## Current State

### What's Working (October 19, 2025)

✅ **Backend:**
- FastAPI server running on port 5000
- PostgreSQL database with PostGIS on Supabase
- 22 tables with full schema
- CRUD operations for projects, drawings, blocks, layers
- DXF import/export functionality

✅ **Frontend:**
- Monolithic dashboard (archived in `archive/dashboard_MISSION_CONTROL_V2.html`)
- Mission Control dark theme (neon blues/purples)
- React components (via CDN)
- Leaflet maps with basemap switching
- Project/drawing management UI

✅ **Infrastructure:**
- GitHub repository (private)
- WSL development environment
- VS Code with remote WSL
- Virtual environment for Python
- Working database connection via Session Pooler

### What Needs to Be Done

🚧 **Restructuring Phase:**
- Split monolithic dashboard into 6 mini-tools
- Extract shared CSS/JS to common files
- Create tool launcher (navigation hub)
- Make each tool LLM-context-window friendly (<30KB)

**Priority tools to extract:**
1. Tool Launcher (hub/homepage)
2. Project Manager (CRUD)
3. Drawing Browser (search/list)
4. Map Viewer (geographic visualization)
5. Drawing Importer (DXF upload)
6. Symbol Library (browse blocks)

---

## Technical Stack

### Backend
```
Framework:      FastAPI 0.119.0
ASGI Server:    Uvicorn 0.38.0
Language:       Python 3.12
Database:       PostgreSQL 14 with PostGIS
Database Host:  Supabase (free tier)
ORM:            None (raw SQL via psycopg2)
```

### Frontend
```
Framework:      React 18 (via CDN, no build step)
Maps:           Leaflet 1.9.4
Styling:        Custom CSS (Mission Control theme)
Transpiler:     Babel Standalone (for JSX in browser)
State:          React useState (local only)
API Calls:      Fetch API
```

### Development Environment
```
OS:             WSL Ubuntu 24.04 on Windows 11
Terminal:       Windows Terminal
Editor:         VS Code with Remote-WSL
VCS:            Git + GitHub
Python Env:     venv (not conda/poetry)
```

---

## Architecture

### Data Flow
```
User Browser
    ↕ HTTP/JSON
FastAPI Server (port 5000)
    ↕ SQL
PostgreSQL/PostGIS (Supabase)
```

### File Structure Philosophy

**Old way (monolithic):**
- One 70KB HTML file with everything
- Hard to edit (LLM context window issues)
- Changes cascade across entire system

**New way (modular):**
- 6 separate tool files (~15-30KB each)
- Shared CSS/JS for common code
- Each tool is independently editable
- Tool Launcher ties everything together

---

## Key Design Decisions

### Why FastAPI?

- Automatic OpenAPI docs (`/docs`)
- Type validation with Pydantic
- Async support for future scaling
- Modern Python framework

### Why React via CDN?

- No build step (simplicity)
- Direct HTML file editing
- LLM-friendly single-file components
- Fast iteration during development

### Why No Build Process?

- **Goal:** Simple, hackable, LLM-friendly
- **Tradeoff:** Slightly larger file sizes
- **Benefit:** Can edit and reload instantly
- **Future:** Can add build step later if needed

### Why Supabase?

- Free tier with PostGIS support
- Managed PostgreSQL (no server maintenance)
- Built-in connection pooling
- Dashboard for database inspection

---

## Database Schema

### Core Tables

**projects**
- Metadata about CAD projects
- Client info, coordinate systems, EPSG codes
- Has many drawings

**drawings**
- Individual DXF files imported
- Links to project
- Stores raw DXF content + parsed geometry
- Has many entities, blocks, layers

**blocks**
- Block definitions (CAD symbols)
- SVG representations
- Metadata (category, domain)
- Used across multiple drawings

**layers**
- Layer definitions with standards
- Color, linetype, lineweight
- Links to layer_standards

### GIS Tables

**gis_parcels**
- Property boundary polygons
- APN, owner, acreage

**gis_roads**
- Road centerlines
- Name, type, speed limit

**gis_buildings**
- Building footprints
- Address, type, stories

### Standards Tables

**layer_standards**
- Standard layer naming conventions
- Discipline.Category.Type format

**linetype_standards**
- Linetype definitions (dashed, dotted, etc.)

**text_styles**
- Text style specifications

---

## API Endpoints

### Base URL
```
http://localhost:5000
```

### Core Routes

**Health/Info:**
```
GET  /                    # Root
GET  /api/health          # Health check + DB status
GET  /api/stats           # System statistics
```

**Projects:**
```
GET    /api/projects                  # List all
POST   /api/projects                  # Create
GET    /api/projects/{id}             # Get one
PUT    /api/projects/{id}             # Update
DELETE /api/projects/{id}             # Delete
GET    /api/projects/{id}/drawings    # Get project's drawings
```

**Drawings:**
```
GET    /api/drawings                  # List all
POST   /api/drawings                  # Create
GET    /api/drawings/{id}             # Get one
PUT    /api/drawings/{id}             # Update
DELETE /api/drawings/{id}             # Delete
GET    /api/drawings/{id}/render      # Get render data
```

**Import/Export:**
```
POST   /api/import/dxf               # Import DXF file
GET    /api/export/{drawing_id}      # Export drawing
```

**Documentation:**
```
GET    /docs                         # Interactive API docs
GET    /openapi.json                 # OpenAPI schema
```

---

## Mission Control Theme

### Color Palette
```css
/* Background */
--bg-primary:   #0a0e27      /* Deep space blue */
--bg-secondary: #1a1f3a      /* Lighter panels */
--bg-hover:     #242946      /* Hover state */

/* Accent Colors */
--accent-cyan:    #00d9ff    /* Primary actions */
--accent-purple:  #b794f6    /* Secondary actions */
--accent-pink:    #f472b6    /* Highlights */

/* Text */
--text-primary:   #e2e8f0    /* Main text */
--text-secondary: #94a3b8    /* Muted text */
--text-dim:       #64748b    /* Very muted */

/* Status */
--success: #10b981
--warning: #f59e0b
--error:   #ef4444
```

### Typography
```css
--font-main:    'Inter', -apple-system, BlinkMacSystemFont, sans-serif
--font-mono:    'JetBrains Mono', 'Fira Code', monospace

/* Sizes */
--text-xs:   0.75rem
--text-sm:   0.875rem
--text-base: 1rem
--text-lg:   1.125rem
--text-xl:   1.25rem
--text-2xl:  1.5rem
```

### Visual Effects
```css
/* Glow effects */
box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);  /* Cyan glow */
box-shadow: 0 0 20px rgba(183, 148, 246, 0.3); /* Purple glow */

/* Glass effect */
background: rgba(26, 31, 58, 0.6);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.1);
```

---

## Coding Patterns

### React Component Structure
```jsx
function ComponentName() {
  // 1. State declarations
  const [data, setData] = React.useState([]);
  const [loading, setLoading] = React.useState(false);
  
  // 2. Effects
  React.useEffect(() => {
    fetchData();
  }, []);
  
  // 3. Event handlers
  const handleSubmit = async (e) => {
    e.preventDefault();
    // ...
  };
  
  // 4. Render
  return (
    <div className="container">
      {/* JSX */}
    </div>
  );
}
```

### API Call Pattern
```javascript
async function fetchProjects() {
  try {
    const response = await fetch('http://localhost:5000/api/projects');
    if (!response.ok) throw new Error('Failed to fetch');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

### Error Handling Pattern
```javascript
try {
  // Operation
  const result = await someOperation();
  showSuccess('Operation completed');
} catch (error) {
  console.error('Error:', error);
  showError(error.message || 'Something went wrong');
}
```

---

## Common Patterns in Codebase

### Database Queries
```python
# Using context manager
with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    result = cur.fetchone()
```

### FastAPI Route
```python
@app.get("/api/projects")
async def get_projects():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
            projects = cur.fetchall()
            return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### React State Update
```javascript
// Correct (immutable)
setProjects([...projects, newProject]);

// Incorrect (mutates state)
projects.push(newProject);
setProjects(projects);
```

---

## Known Quirks & Gotchas

### Database Connection

⚠️ **Must use Session Pooler:**
- Host: `aws-1-us-east-2.pooler.supabase.com`
- NOT: `db.dkvyhbqmeumanhnhxmxf.supabase.co`
- Reason: IPv6 not configured in WSL

⚠️ **User format matters:**
- Correct: `postgres.dkvyhbqmeumanhnhxmxf`
- Wrong: `postgres`

### React in Browser

⚠️ **JSX requires Babel:**
```html
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<script type="text/babel">
  // JSX code here
</script>
```

⚠️ **Script loading order:**
1. React
2. ReactDOM
3. Other libraries (Leaflet, etc.)
4. Babel
5. Your code (type="text/babel")

### CORS in Development

⚠️ **API must allow localhost:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## File Naming Conventions

### Backend (Python)
```
snake_case.py           # Python modules
api_server_ENHANCED.py  # Main files (descriptive)
```

### Frontend (HTML/JS/CSS)
```
kebab-case.html         # HTML files
kebab-case.js           # JavaScript files
kebab-case.css          # CSS files

# Examples:
project-manager.html
drawing-importer.html
map-viewer.html
```

### Documentation (Markdown)
```
SCREAMING_SNAKE_CASE.md    # Major docs
README.md                  # Entry point
TROUBLESHOOTING.md         # Reference guides
```

---

## Testing Strategy

### Manual Testing (Current)

1. Start API server
2. Open tool in browser
3. Perform operations
4. Check console for errors
5. Verify in Supabase dashboard

### Future: Automated Testing
```bash
# API tests
pytest tests/test_api.py

# Frontend tests (future)
# Would need build setup for this
```

---

## Deployment Considerations (Future)

### Current: Local Development Only

- API runs on localhost:5000
- HTML files opened via `file://` or served locally
- Database on Supabase (already cloud)

### Future: Production Deployment

**Backend options:**
- Heroku / Railway / Fly.io
- AWS EC2 / DigitalOcean
- Containerize with Docker

**Frontend options:**
- Static hosting: Netlify / Vercel / GitHub Pages
- Same server as backend (serve static files)

**Database:**
- Upgrade Supabase to paid tier
- Or migrate to self-hosted PostgreSQL

---

## Working with LLMs (Like Claude Code)

### What to Provide

**Always include:**
1. What you're trying to accomplish
2. Current file(s) being worked on
3. Error messages (full traceback)
4. Relevant environment info

**Example request:**
```
I'm working on extracting the Project Manager tool from the monolithic 
dashboard. I need to:

1. Create frontend/tools/project-manager.html
2. Extract the ProjectManager React component from archive/dashboard_MISSION_CONTROL_V2.html
3. Use shared styles from frontend/shared/styles.css
4. Call /api/projects endpoints

Current error: [paste error]

Environment: WSL, Python 3.12, FastAPI, React via CDN
```

### What NOT to Do

❌ "Make it work" (too vague)  
❌ Paste entire 70KB file (too large)  
❌ "Fix this" without context  
❌ Request without error messages

### Best Practices

✅ Be specific about goals  
✅ Include relevant code snippets  
✅ Mention constraints (file size, dependencies)  
✅ Reference this document for context

---

## Glossary

**DXF:** Drawing Exchange Format (AutoCAD's open file format)  
**PostGIS:** PostgreSQL extension for geographic data  
**EPSG:** European Petroleum Survey Group (coordinate system codes)  
**CRUD:** Create, Read, Update, Delete  
**ASGI:** Asynchronous Server Gateway Interface  
**CDN:** Content Delivery Network  
**JSX:** JavaScript XML (React's syntax)  
**Supabase:** Backend-as-a-Service (managed PostgreSQL)  
**Session Pooler:** Connection pooling service (IPv4 compatible)

---

## Quick Facts for LLMs
```
Project:        acad-gis
Language:       Python 3.12 (backend), JavaScript (frontend)
Framework:      FastAPI + React (CDN)
Database:       PostgreSQL 14 + PostGIS (Supabase)
Location:       ~/projects/acad-gis (WSL)
GitHub:         https://github.com/Rtoony/acad-gis
API Port:       5000
Files:          22 database tables, 6 tools (to be created)
Current Phase:  Restructuring from monolithic to modular
```

---

## Related Documentation

**For setup:**
- WSL_SETUP.md
- DEVELOPMENT_ENVIRONMENT.md
- DATABASE_CONNECTION.md

**For daily work:**
- GIT_WORKFLOW.md

**For reference:**
- SETUP_GUIDE.md (original)
- DATABASE_SCHEMA_GUIDE.md
- TROUBLESHOOTING.md

---

**Last Updated:** October 19, 2025  
**Status:** ✅ Environment configured, ready for tool extraction  
**Next Task:** Create Tool Launcher and extract first mini-tool
