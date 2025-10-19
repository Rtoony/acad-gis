# ACAD=GIS - CAD Database Management System

**Version:** 2.0  
**Mission Control** - Modular Tool Architecture

## 🎯 What is ACAD=GIS?

ACAD=GIS is a web-based CAD database management system that bridges AutoCAD drawings with PostgreSQL database storage and GIS visualization. It provides a suite of specialized tools for managing projects, importing DXF files, viewing georeferenced drawings on interactive maps, and managing symbol libraries.

## ✨ Key Features

- **Project Management** - Organize drawings by project with metadata tracking
- **DXF Import** - Process and import AutoCAD DXF files with georeferencing support
- **GIS Integration** - View CAD drawings on interactive maps with real GIS layer overlays
- **Symbol Library** - Manage and browse CAD block definitions as SVG symbols
- **PostgreSQL Backend** - Structured database storage with vector similarity search (pgvector)
- **RESTful API** - Complete CRUD operations for all entities

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 13+ with pgvector extension
- Modern web browser (Chrome, Firefox, Edge)

### 1. Clone or Download

```bash
git clone <repository-url>
cd ACAD_GIS
```

### 2. Set Up Database

```bash
# Create PostgreSQL database
createdb acad_gis

# Run schema setup
psql -d acad_gis -f database/schema.sql
```

### 3. Configure Environment

Create a `.env` file in the backend directory:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=acad_gis
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Start API Server

```bash
cd backend
python api_server_ENHANCED.py
```

The API will start on `http://localhost:8000`

### 6. Open Tool Launcher

Open `tool_launcher.html` in your browser. This is your central hub for accessing all tools.

**💡 Tip:** Bookmark the Tool Launcher or set it as your browser homepage for quick access!

## 📁 Project Structure

```
ACAD_GIS/
├── tool_launcher.html              # 🏠 START HERE - Central navigation hub
│
├── backend/
│   ├── api_server_ENHANCED.py      # FastAPI REST server
│   ├── database.py                 # Database connection & queries
│   ├── import_dxf_georef.py        # DXF processing script
│   └── .env                        # Database configuration (you create this)
│
├── frontend/
│   ├── tools/
│   │   ├── project_manager.html    # ✅ Create/edit/delete projects
│   │   ├── drawing_browser.html    # ✅ Search and browse drawings
│   │   ├── map_viewer.html         # ✅ View drawings on maps with GIS
│   │   ├── drawing_importer.html   # ✅ Upload and process DXF files
│   │   └── symbol_library.html     # 🔜 Browse block definitions
│   │
│   └── shared/
│       ├── styles.css              # Mission Control theme
│       └── components.js           # Reusable React components
│
├── docs/
│   ├── README.md                   # This file
│   ├── SETUP_GUIDE.md              # Detailed installation guide
│   ├── USER_GUIDE.md               # How to use each tool
│   ├── API_REFERENCE.md            # API documentation
│   └── ARCHITECTURE.md             # System design overview
│
└── database/
    └── schema.sql                  # PostgreSQL schema definition
```

## 🛠️ Available Tools

### 1. Tool Launcher (Central Hub)
- Navigate to all tools
- View system statistics
- Check API connection status
- See recent activity
- Quick action buttons

### 2. Project Manager
**Purpose:** Create, edit, and organize projects  
**Features:**
- Create new projects with client info
- Edit project metadata
- Delete projects
- View project statistics
- Group drawings by project

### 3. Drawing Browser
**Purpose:** Search and browse all drawings  
**Features:**
- Full-text search across drawings
- Filter by project, name, or number
- List and grid view options
- Quick actions (view, edit, delete)
- Drawing metadata display

### 4. Map Viewer
**Purpose:** View drawings on interactive maps  
**Features:**
- Georeferenced drawing overlay
- Multiple basemap options (Streets, Satellite, Topo)
- GIS layer integration (Parcels, Roads, Buildings)
- Interactive symbol popups
- Layer visibility controls
- Coordinate transformation (EPSG:2226 → WGS84)

### 5. Drawing Importer
**Purpose:** Upload and process DXF files  
**Features:**
- Drag-and-drop DXF upload
- Project association
- Georeferencing configuration
- EPSG code specification
- Processing progress tracking
- Automatic symbol extraction

### 6. Symbol Library (Coming Soon)
**Purpose:** Browse and manage symbols  
**Planned Features:**
- Visual symbol browser
- Category/domain filtering
- SVG preview
- Metadata display
- Usage statistics

## 🎨 Design Philosophy

### Modular Architecture
Each tool is a **standalone HTML file** (~15-30KB) that:
- Serves a single, focused purpose
- Imports shared styling and components
- Communicates with the unified API
- Can be modified independently
- Fits in LLM context windows for easy AI-assisted development

### Shared Foundation
All tools use:
- **shared/styles.css** - Mission Control theme with neon accents
- **shared/components.js** - Reusable React components and API helpers
- **Unified API** - Single backend server for all operations

### Benefits
- ✅ Easy to maintain (change styles once, affects all tools)
- ✅ Fast development (build tools independently)
- ✅ LLM-friendly (small files for AI collaboration)
- ✅ Modular (mix and match tools as needed)
- ✅ Consistent UX (shared components and styling)

## 🔌 API Endpoints

The API server provides RESTful endpoints for all operations:

### Health & Stats
- `GET /api/health` - Check API status
- `GET /api/stats` - Get system statistics

### Projects
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get project details
- `POST /api/projects` - Create project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Drawings
- `GET /api/drawings` - List all drawings
- `GET /api/drawings/{id}` - Get drawing details
- `GET /api/drawings/{id}/render` - Get drawing render data
- `POST /api/drawings` - Create drawing
- `PUT /api/drawings/{id}` - Update drawing
- `DELETE /api/drawings/{id}` - Delete drawing

### Import/Export
- `POST /api/import/dxf` - Upload and import DXF file

**Full API documentation:** See [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

## 🗺️ GIS Integration

ACAD=GIS includes powerful GIS features for georeferenced drawings:

### Supported Coordinate Systems
- **EPSG:2226** - California State Plane Zone III (US Survey Feet)
- Automatic transformation to WGS84 for web mapping

### Available GIS Layers
- **Sonoma County Parcels** - Property boundaries and ownership
- **Streets & Roads** - Road network with classifications
- **Buildings** - Building footprints with attributes

### Basemap Options
- Streets (Esri World Street Map)
- Satellite (Esri World Imagery)
- OpenStreetMap
- Topographic (OpenTopoMap)

## 📊 Database Schema

Core tables:
- `projects` - Project information
- `drawings` - Drawing files and metadata
- `layers` - CAD layers with styling
- `block_definitions` - Symbol/block definitions with SVG
- `block_inserts` - Symbol placements in drawings
- `layer_standards` - Standard layer definitions

Uses **pgvector** extension for semantic similarity search.

## 🔧 Configuration

### Database Connection
Edit `backend/.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=acad_gis
DB_USER=postgres
DB_PASSWORD=your_secure_password
```

### API Server
Default port: `8000`  
To change: Edit `api_server_ENHANCED.py` (last line)

### Frontend Tools
API URL is configured in `shared/components.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

## 🚦 Workflow Examples

### Morning Workflow
1. Open Tool Launcher (bookmarked)
2. Check API status indicator (green = ready)
3. Review statistics and recent activity
4. Click "Browse Drawings" card
5. Search/filter to find drawing
6. Click drawing to open in Map Viewer

### Import New Drawing
1. Open Tool Launcher
2. Click "Import Drawing" quick action
3. Drag DXF file to upload area
4. Select project and set georeferencing
5. Click "Process Drawing"
6. View imported drawing in Map Viewer

### Create New Project Workflow
1. Open Tool Launcher
2. Click "Create New Project" quick action
3. Enter project details
4. Save project
5. Import drawings for project
6. Organize and view in Drawing Browser

## 🐛 Troubleshooting

### API Won't Start
- Check PostgreSQL is running
- Verify `.env` file exists with correct credentials
- Check port 8000 is not in use
- Review console for error messages

### Database Connection Failed
- Verify PostgreSQL service is running
- Check database name, user, and password
- Ensure pgvector extension is installed
- Test connection: `psql -U postgres -d acad_gis`

### Tools Can't Connect to API
- Verify API server is running (check console)
- Check browser console for CORS errors
- Ensure API_BASE_URL in components.js is correct
- Try accessing `http://localhost:8000/api/health` directly

### Drawings Not Displaying
- Check drawing has block_inserts in database
- Verify symbols have SVG content
- Check browser console for JavaScript errors
- Ensure drawing_id is valid

## 📚 Documentation

- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Detailed installation instructions
- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - Step-by-step usage tutorials
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete API documentation
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and data flow

## 🎯 Roadmap

### Phase 1: Foundation (Complete ✅)
- [x] Shared styling system
- [x] Shared components library
- [x] Tool Launcher hub
- [x] Project structure reorganization

### Phase 2: Core Tools (In Progress)
- [x] Project Manager
- [x] Drawing Browser
- [x] Map Viewer
- [x] Drawing Importer
- [ ] Symbol Library

### Phase 3: Advanced Features (Planned)
- [ ] Batch operations
- [ ] Export to DXF/GeoJSON
- [ ] Advanced search with filters
- [ ] User authentication
- [ ] Drawing comparison tool
- [ ] Annotation system

### Phase 4: Polish (Future)
- [ ] Mobile responsive design
- [ ] Offline support
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Video tutorials

## 🤝 Contributing

This is a personal/internal project, but suggestions are welcome!

To add a new tool:
1. Create HTML file in `frontend/tools/`
2. Import `shared/styles.css` and `shared/components.js`
3. Add tool card to `tool_launcher.html`
4. Follow naming convention: `tool_name.html`

## 📄 License

Internal use only. All rights reserved.

## 💡 Tips & Tricks

### Desktop Shortcut
Create a `.bat` file to launch everything:
```batch
@echo off
start "" "http://localhost/ACAD_GIS/tool_launcher.html"
cd C:\path\to\ACAD_GIS\backend
start python api_server_ENHANCED.py
```

### Browser Setup
1. Bookmark Tool Launcher
2. Set as homepage for instant access
3. Enable "Open links in new tab" for tool navigation

### Development Workflow
- Use browser DevTools (F12) for debugging
- Check API responses in Network tab
- View React state in Components tab
- Test with small datasets first

### Performance
- Database queries are optimized with indexes
- Drawing rendering limits to 2500 symbols by default
- GIS layers load on-demand
- API responses are cached where appropriate

## 🆘 Support

For issues or questions:
1. Check documentation in `docs/` folder
2. Review browser console for errors
3. Check API server logs
4. Verify database connection
5. Search existing issues/documentation

## 🏆 Credits

Built with:
- **React** - UI framework
- **FastAPI** - Python web framework
- **PostgreSQL + pgvector** - Database
- **Leaflet** - Interactive maps
- **Esri Leaflet** - GIS integration
- **Font Awesome** - Icons

---

**ACAD=GIS © 2025** • Built for efficient CAD data management and GIS visualization
