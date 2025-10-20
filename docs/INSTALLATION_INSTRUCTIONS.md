# Phase 2.1 Installation Instructions

**What:** DataTable Component and React Component Library  
**When:** Install these files now to use in your tools  
**Where:** Your ACAD-GIS project (`H:\acad-gis\` or `/mnt/h/acad-gis/`)

---

## 📦 What You're Installing

**4 New Files:**
1. `react-components.js` - All React components including DataTable
2. `styles.css` - Updated with DataTable styles
3. `datatable-demo.html` - Live demo/test file
4. `COMPONENT_LIBRARY.md` - Complete documentation

---

## 🚀 Quick Install (5 Minutes)

### Step 1: Download Files from Claude

All files are in the `/mnt/user-data/outputs/` folder. Download them to your computer.

### Step 2: Copy to Your Project

**In WSL:**
```bash
# Navigate to your project
cd /mnt/h/acad-gis

# Create demo directory if needed
mkdir -p frontend/demos

# Copy files (adjust paths if you downloaded elsewhere)
# You'll need to move the downloaded files from Windows to these locations
```

**File destinations:**
```
H:\acad-gis\
├── frontend\
│   ├── shared\
│   │   ├── components.js           ← KEEP (already exists)
│   │   ├── react-components.js     ← ADD (new file)
│   │   └── styles.css              ← REPLACE (updated version)
│   │
│   └── demos\
│       └── datatable-demo.html     ← ADD (new file)
│
└── docs\
    └── COMPONENT_LIBRARY.md        ← ADD (new file)
```

### Step 3: Test the Installation

**Open the demo:**
1. Navigate to `H:\acad-gis\frontend\demos\`
2. Double-click `datatable-demo.html`
3. Should open in browser with working DataTable

**Expected result:**
- Page loads with Mission Control theme ✅
- Stats cards show (4 cards at top) ✅
- DataTable displays 8 mock projects ✅
- Search box works ✅
- Column headers are clickable (sorting) ✅
- Pagination controls visible ✅
- Action buttons work ✅

---

## 📝 Detailed Installation Steps

### Option A: Manual Copy (Recommended)

**1. Create the directory structure:**
```bash
cd /mnt/h/acad-gis

# Ensure directories exist
mkdir -p frontend/shared
mkdir -p frontend/demos
mkdir -p docs
```

**2. Copy `react-components.js`:**
- Download from outputs
- Copy to: `H:\acad-gis\frontend\shared\react-components.js`

**3. Replace `styles.css`:**
- **BACKUP OLD FILE FIRST:**
  ```bash
  cp frontend/shared/styles.css frontend/shared/styles.css.backup
  ```
- Download new styles.css from outputs
- Copy to: `H:\acad-gis\frontend\shared\styles.css`

**4. Copy `datatable-demo.html`:**
- Download from outputs
- Copy to: `H:\acad-gis\frontend\demos\datatable-demo.html`

**5. Copy `COMPONENT_LIBRARY.md`:**
- Download from outputs
- Copy to: `H:\acad-gis\docs\COMPONENT_LIBRARY.md`

### Option B: Direct File Creation

If you have the file contents, you can create them directly in WSL:

```bash
cd /mnt/h/acad-gis/frontend/shared

# Create react-components.js
nano react-components.js
# Paste content, Ctrl+X, Y, Enter

# Backup and update styles.css
cp styles.css styles.css.backup
nano styles.css
# Paste content, Ctrl+X, Y, Enter
```

---

## ✅ Verification Checklist

After installation, verify:

### File Structure Check
```bash
cd /mnt/h/acad-gis

# List frontend files
ls -la frontend/shared/
# Should show: components.js, react-components.js, styles.css

# List demo files
ls -la frontend/demos/
# Should show: datatable-demo.html

# List docs
ls -la docs/
# Should see: COMPONENT_LIBRARY.md
```

### Functional Test
1. **Open demo in browser:**
   - File: `H:\acad-gis\frontend\demos\datatable-demo.html`
   - Should load without errors

2. **Check browser console (F12):**
   - Should see: ✅ ACAD=GIS utilities loaded
   - Should see: ✅ ACAD=GIS React components loaded
   - Should see: 📦 Available components: DataTable, Modal, ...
   - No errors in red

3. **Test features:**
   - [ ] Search box filters data
   - [ ] Click column headers to sort
   - [ ] Pagination buttons work
   - [ ] Action buttons show toasts
   - [ ] Modal opens when clicking "View"
   - [ ] Hover effects on rows

---

## 🔧 Troubleshooting

### Problem: Demo page is blank

**Check:**
1. Open browser console (F12)
2. Look for errors

**Common fixes:**
- **Missing React:** Ensure React CDN loads
- **Wrong file paths:** Check that styles.css and components.js paths are correct
- **Cached files:** Hard refresh (Ctrl+F5)

### Problem: Components not loading

**Error:** `DataTable is not defined`

**Fix:**
```html
<!-- Ensure correct order -->
<script src="../shared/components.js"></script>      <!-- First -->
<script src="../shared/react-components.js"></script> <!-- Second -->
<script type="text/babel">                           <!-- Third -->
    // Your code here
</script>
```

### Problem: Styles not applying

**Check:**
1. `styles.css` is updated version (should have `.datatable` styles)
2. File path in HTML is correct: `<link rel="stylesheet" href="../shared/styles.css">`
3. Clear browser cache (Ctrl+Shift+R)

### Problem: Can't find downloaded files

**Solution:**
Files are in Claude's outputs folder. You need to:
1. View the files in this chat
2. Copy content to clipboard
3. Create files manually in your project

**Or use the download links provided in this chat.**

---

## 📚 After Installation

### Next Steps

**Option 1: Test the DataTable (Recommended)**
1. Open `datatable-demo.html`
2. Play with search, sort, pagination
3. Click action buttons
4. Read through the code to understand usage

**Option 2: Start Building Project Manager**
1. Create `frontend/tools/project_manager.html`
2. Copy template from COMPONENT_LIBRARY.md
3. Add DataTable with project data
4. Connect to your API

**Option 3: Continue Phase 2**
Follow DEVELOPMENT_ROADMAP.md to build Form Components next

### Documentation to Read

1. **COMPONENT_LIBRARY.md** - API reference for all components
2. **PHASE_2_1_COMPLETE.md** - What was built and why
3. **DEVELOPMENT_ROADMAP.md** - Next phases
4. **QUICK_REFERENCE.md** - Code snippets and patterns

---

## 🎯 Using DataTable in Your Tools

### Basic Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="../shared/styles.css">
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="grid-background">
    <div id="root"></div>
    
    <script src="../shared/components.js"></script>
    <script src="../shared/react-components.js"></script>
    
    <script type="text/babel">
        const { useState, useEffect } = React;
        
        function MyTool() {
            const [data, setData] = useState([]);
            const [loading, setLoading] = useState(true);
            
            useEffect(() => {
                loadData();
            }, []);
            
            const loadData = async () => {
                const result = await api.get('/your-endpoint');
                setData(result);
                setLoading(false);
            };
            
            const columns = [
                { key: 'name', label: 'Name' },
                { key: 'created_at', label: 'Created', format: 'date' }
            ];
            
            return React.createElement('div', { className: 'page-wrapper' },
                React.createElement(Header, {
                    title: 'My Tool',
                    showBackButton: true
                }),
                React.createElement('main', { className: 'main-content' },
                    React.createElement('div', { className: 'container' },
                        React.createElement(DataTable, {
                            data: data,
                            columns: columns,
                            loading: loading
                        })
                    )
                ),
                React.createElement(Footer)
            );
        }
        
        ReactDOM.createRoot(document.getElementById('root')).render(
            React.createElement(MyTool)
        );
    </script>
</body>
</html>
```

---

## 🎓 Learning Resources

### Understanding the Code

1. **Start with demo:** Open `datatable-demo.html` and read through it
2. **Examine component:** Open `react-components.js` and find the DataTable component
3. **Try modifications:** Change pageSize, add columns, modify data

### React Concepts Used

- **useState** - Managing component state
- **useEffect** - Loading data on mount
- **useMemo** - Performance optimization
- **React.createElement** - Creating elements without JSX

---

## ✅ Installation Complete Checklist

- [ ] All 4 files copied to correct locations
- [ ] `datatable-demo.html` opens in browser
- [ ] No console errors
- [ ] DataTable displays and works
- [ ] Search, sort, pagination all functional
- [ ] Documentation accessible
- [ ] Ready to use in your own tools

---

## 📞 Need Help?

### Common Questions

**Q: Do I need to restart API server?**  
A: No, these are frontend-only changes.

**Q: Will this break existing code?**  
A: No, `components.js` is unchanged. `styles.css` is backward compatible.

**Q: Can I use old dashboard still?**  
A: Yes, old dashboard is unaffected.

**Q: How big are these files?**  
A: Total ~40KB (similar to a few images).

### Debugging

If something doesn't work:
1. Check browser console (F12) for errors
2. Verify file paths in HTML
3. Try demo file first to ensure base installation works
4. Check that React CDN is accessible

---

## 🚀 You're Ready!

Once installation is complete:
- ✅ DataTable component available in all tools
- ✅ 12 React components ready to use
- ✅ Mission Control styling applied
- ✅ Complete documentation available
- ✅ Demo file for testing and learning

**Next:** Build your first tool using DataTable, or continue to Phase 2.2 (Form Components)!

---

**Installation Guide Version:** 1.0  
**Date:** October 19, 2025  
**Status:** Ready for installation
