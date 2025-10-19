# ACAD=GIS Project Structure

## Current Foundation (Complete ✅)

```
ACAD_GIS/
├── tool_launcher.html              ✅ CREATED - Central hub, START HERE
│
├── shared/
│   ├── styles.css                  ✅ CREATED - Mission Control theme
│   └── components.js               ✅ CREATED - Reusable components & API helpers
│
├── README.md                       ✅ CREATED - Main documentation
│
└── [Your existing files]
    ├── dashboard_MISSION_CONTROL_V2.html    (Reference for extraction)
    ├── api_server_ENHANCED.py               (Working API server)
    └── database.py                          (Database helpers)
```

## What We Built

### 1. **shared/styles.css** (~15KB)
Complete Mission Control styling system:
- CSS variables for consistent theming
- Dark mode with neon glows
- Animated grid background
- Card, button, form components
- Modal and alert styles
- Status indicators
- Loading spinners
- Responsive grid layouts
- Custom scrollbars

**Usage in tools:**
```html
<link rel="stylesheet" href="../shared/styles.css">
```

### 2. **shared/components.js** (~10KB)
Reusable React components and utilities:
- **Components:**
  - `ApiStatus` - Connection indicator
  - `LoadingSpinner` - Loading states
  - `Alert` - Success/error messages
  - `Modal` - Dialog boxes
  - `ConfirmDialog` - Confirmation prompts
  - `EmptyState` - No data displays
  - `StatCard` - Statistics display
  - `Header` - Page headers
  - `Footer` - Page footers
  - `SearchBar` - Search inputs
  - `Badge` - Status badges
  - `ToastManager` - Toast notifications

- **API Helpers:**
  - `api.get()`, `api.post()`, `api.put()`, `api.delete()`
  - `api.upload()` for file uploads
  - `api.checkHealth()` for status checks

- **Utilities:**
  - `formatDate()` - Date formatting
  - `debounce()` - Input debouncing
  - `copyToClipboard()` - Copy text
  - `downloadFile()` - File downloads

**Usage in tools:**
```html
<script src="../shared/components.js"></script>
```

### 3. **tool_launcher.html** (~8KB)
Central navigation hub:
- Tool cards with icons and descriptions
- System statistics dashboard
- Recent activity feed
- Quick action buttons
- API status monitoring
- Responsive grid layout
- Opens tools in new tabs

**Features:**
- Shows total projects, drawings, symbols, layers
- Displays recent drawing activity
- Provides quick access to common actions
- Clean, intuitive interface
- Auto-refreshes statistics

### 4. **README.md** (~12KB)
Comprehensive project documentation:
- Project overview and features
- Quick start guide (6 steps)
- Project structure explanation
- Tool descriptions
- API endpoint reference
- GIS integration details
- Workflow examples
- Troubleshooting guide
- Roadmap and future plans

## Next Steps: Creating Individual Tools

### Phase 1: Extract Core Tools from V2 Dashboard

#### 1. Project Manager (~20KB)
**Extract from:** V2 Dashboard → Projects Tab

**Features to include:**
- Project list with cards
- Create project modal
- Edit project modal
- Delete with confirmation
- Project statistics (drawing count)
- Search/filter functionality

**Template structure:**
```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="../shared/styles.css">
    <!-- React, Font Awesome -->
</head>
<body class="grid-background">
    <div id="root"></div>
    <script src="../shared/components.js"></script>
    <script type="text/babel">
        function ProjectManager() {
            // State: projects, loading, modals
            // Functions: CRUD operations
            // Render: Header, search, project grid, modals
        }
    </script>
</body>
</html>
```

#### 2. Drawing Browser (~20KB)
**Extract from:** V2 Dashboard → Projects Tab (drawings view)

**Features to include:**
- Drawing list/grid views
- Search by name, number, project
- Filter by project
- Quick view/edit/delete actions
- Drawing metadata display
- Link to Map Viewer

**Key differences from V2:**
- Focused only on browsing/searching
- No embedded map viewer
- Links open Map Viewer in new tab
- Cleaner, more focused interface

#### 3. Map Viewer (~30KB)
**Extract from:** V2 Dashboard → Drawing Viewer Tab

**Features to include:**
- Interactive Leaflet map
- Drawing selection dropdown
- Layer visibility toggles
- GIS layer overlays (Parcels, Roads, Buildings)
- Basemap switching
- Symbol popups with metadata
- Georeferencing support
- CAD coordinate display

**This is the largest tool because:**
- Leaflet map initialization
- Coordinate transformation logic
- GIS layer configuration
- Symbol rendering (SVG markers)

#### 4. Drawing Importer (~15KB)
**Create new tool** (not in V2 dashboard)

**Features to include:**
- Drag-and-drop file upload
- Project selection dropdown
- Georeferencing options:
  - Checkbox: "Is Georeferenced?"
  - EPSG code input
  - Coordinate system selector
- File upload progress
- Success/error handling
- Link to view imported drawing

**API integration:**
```javascript
const formData = new FormData();
formData.append('file', fileObject);
formData.append('project_id', selectedProjectId);
formData.append('is_georeferenced', true);
formData.append('epsg_code', 'EPSG:2226');
await api.upload('/import/dxf', formData);
```

### Phase 2: Build Specialized Tools

#### 5. Symbol Library (~15KB)
**New tool** - Browse block definitions

**Features:**
- Grid/list of symbols
- SVG preview cards
- Filter by category/domain
- Search by name
- Symbol metadata display
- Usage statistics
- Related drawings link

**Data structure:**
```javascript
{
    block_id: "uuid",
    block_name: "TREE-01",
    svg_content: "<circle...>",
    category: "Landscape",
    domain: "Site Planning",
    usage_count: 42
}
```

## Implementation Strategy

### Week 1: Foundation Complete ✅
- [x] Create shared/styles.css
- [x] Create shared/components.js
- [x] Create tool_launcher.html
- [x] Write README.md

### Week 2: Core Tools (Current Phase)
**Day 1-2: Project Manager**
1. Copy V2 ProjectsTab component
2. Strip down to essentials
3. Integrate with shared components
4. Test CRUD operations
5. Polish UI

**Day 3-4: Drawing Browser**
1. Copy V2 drawing display logic
2. Add search/filter UI
3. Remove embedded viewer
4. Add "View in Map" links
5. Test with large datasets

**Day 5-7: Map Viewer**
1. Copy V2 DrawingViewerTab
2. Extract map initialization
3. Keep all GIS features
4. Simplify UI (focused on viewing)
5. Test georeferencing

### Week 3: Import & Library
**Day 1-3: Drawing Importer**
1. Design upload UI
2. Add drag-and-drop
3. Implement file upload
4. Add georeferencing controls
5. Test with sample DXF files

**Day 4-7: Symbol Library**
1. Design symbol grid
2. Fetch block_definitions
3. Add SVG preview
4. Implement filtering
5. Add usage statistics

## Tool Size Targets

| Tool | Target Size | Status |
|------|-------------|--------|
| Tool Launcher | 8-10KB | ✅ 8KB |
| Project Manager | 18-22KB | ⏳ Pending |
| Drawing Browser | 18-22KB | ⏳ Pending |
| Map Viewer | 28-32KB | ⏳ Pending |
| Drawing Importer | 15-18KB | ⏳ Pending |
| Symbol Library | 15-18KB | ⏳ Pending |
| **Shared Files** | 25KB | ✅ Complete |
| **Total System** | ~130-150KB | Target |

Compare to V2 Dashboard: **~70KB monolithic**

Benefits of modular approach:
- Each tool fits in LLM context window
- Easier to modify and test
- Better separation of concerns
- Can work on tools independently
- Users can mix and match tools

## File Organization

### Current Structure
```
C:\Users\Josh\Desktop\ACAD_GIS\
├── tool_launcher.html
├── shared\
│   ├── styles.css
│   └── components.js
├── backend\
│   ├── api_server_ENHANCED.py
│   ├── database.py
│   └── import_dxf_georef.py
└── [legacy files to organize]
```

### Target Structure (End of Phase 2)
```
C:\Users\Josh\Desktop\ACAD_GIS\
├── tool_launcher.html              # START HERE
│
├── frontend\
│   ├── tools\
│   │   ├── project_manager.html
│   │   ├── drawing_browser.html
│   │   ├── map_viewer.html
│   │   ├── drawing_importer.html
│   │   └── symbol_library.html
│   │
│   └── shared\
│       ├── styles.css
│       └── components.js
│
├── backend\
│   ├── api_server_ENHANCED.py
│   ├── database.py
│   ├── import_dxf_georef.py
│   └── .env
│
├── docs\
│   ├── README.md
│   ├── SETUP_GUIDE.md
│   ├── USER_GUIDE.md
│   ├── API_REFERENCE.md
│   └── ARCHITECTURE.md
│
├── database\
│   └── schema.sql
│
└── archive\
    └── original_dashboard\
        └── dashboard_MISSION_CONTROL_V2.html
```

## Usage Patterns

### Opening Tools
Users can open tools three ways:

1. **From Tool Launcher** (Recommended)
   - Click tool card
   - Opens in new tab
   - Maintains launcher as home base

2. **Direct URL**
   - Bookmark specific tools
   - `file:///path/to/frontend/tools/project_manager.html`

3. **Quick Actions**
   - Launcher has quick action buttons
   - "Create Project" → Opens Project Manager
   - "Import Drawing" → Opens Drawing Importer

### Navigation Flow
```
Tool Launcher (Home Base)
    ↓
    ├─→ Project Manager → Create Project → Back to Launcher
    ├─→ Drawing Browser → Search → Open in Map Viewer
    ├─→ Map Viewer → View Drawing → Back to Browser
    ├─→ Drawing Importer → Upload → View in Map Viewer
    └─→ Symbol Library → Browse → Back to Launcher
```

## Testing Checklist

### Foundation Testing ✅
- [x] Tool Launcher loads without errors
- [x] API status indicator works
- [x] Statistics display correctly
- [x] Tool cards are clickable
- [x] Quick actions function
- [x] Shared styles apply correctly
- [x] Components load and render

### Per-Tool Testing (Template)
- [ ] Tool loads without errors
- [ ] API connection indicator works
- [ ] Data loads from API
- [ ] CRUD operations work
- [ ] Forms validate correctly
- [ ] Modals open and close
- [ ] Search/filter functions
- [ ] Error handling works
- [ ] Loading states display
- [ ] Back button works

## Development Tips

### Working with LLMs
1. **Attach V2 Dashboard for reference**
   - Shows complete working examples
   - Extract components from it

2. **Attach target tool skeleton**
   - LLM fills in functionality
   - Maintains consistent structure

3. **Test incrementally**
   - Build one feature at a time
   - Test after each addition

### Common Patterns

**Every tool should have:**
```javascript
// State management
const [data, setData] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

// Data loading
useEffect(() => {
    loadData();
}, []);

// API calls with error handling
const loadData = async () => {
    setLoading(true);
    try {
        const result = await api.get('/endpoint');
        setData(result);
    } catch (err) {
        setError(err.message);
        ToastManager.error('Failed to load data');
    } finally {
        setLoading(false);
    }
};

// Render structure
return (
    <div className="page-wrapper">
        <Header title="Tool Name" showBackButton />
        <main className="main-content">
            {loading ? <LoadingSpinner /> : <DataDisplay />}
        </main>
        <Footer />
    </div>
);
```

## Success Criteria

Foundation is complete when:
- ✅ Shared styles work across all tools
- ✅ Shared components are reusable
- ✅ Tool Launcher provides central navigation
- ✅ Documentation is comprehensive
- ✅ File structure is organized

Each tool is complete when:
- [ ] Loads without errors
- [ ] Connects to API successfully
- [ ] Performs its core function
- [ ] Has proper error handling
- [ ] Uses shared components
- [ ] Follows design patterns
- [ ] Fits size target (~15-30KB)
- [ ] Works independently

## Next Step

**Ready to build Project Manager!**

Files needed:
1. Reference: `dashboard_MISSION_CONTROL_V2.html` (extract ProjectsTab)
2. Template: Create `frontend/tools/project_manager.html`
3. API: Already working in `api_server_ENHANCED.py`
4. Database: Already configured in `database.py`

Let's do it! 🚀
