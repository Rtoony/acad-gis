# Frontend Testing Checklist

Use this checklist to manually test your frontend tools.

**How to use:** Go through each section and check off items that work. Note any issues you find.

---

## Tool Launcher (`tool_launcher.html`)

**Open:** `file:///home/user/acad-gis/tool_launcher.html`

- [ ] Page loads without errors
- [ ] No errors in browser console (press F12 → Console tab)
- [ ] All 12 tool cards are visible
- [ ] Stats display correctly (project count, drawing count)
- [ ] Recent activity section loads
- [ ] Clicking each card opens the correct tool

**Issues found:**
```
(Write any issues here)
```

---

## Project Manager (`frontend/tools/project-manager.html`)

- [ ] Opens without errors
- [ ] "Back to Launcher" button works
- [ ] Can see list of projects
- [ ] Can create new project
- [ ] Can edit existing project
- [ ] Can delete project
- [ ] Search box works
- [ ] Sort columns work (click headers)
- [ ] Pagination works (if >20 projects)

**Issues found:**
```
(Write any issues here)
```

---

## Drawings Manager (`frontend/tools/drawings-manager.html`)

- [ ] Opens without errors
- [ ] Can see list of drawings
- [ ] Can filter by project
- [ ] Search works
- [ ] Can view drawing details
- [ ] Can edit drawing
- [ ] Can delete drawing

**Issues found:**
```
(Write any issues here)
```

---

## Map Viewer (`frontend/tools/map_viewer.html`)

- [ ] Opens without errors
- [ ] Project dropdown populates with projects
- [ ] Can select a project
- [ ] Map loads (see map tiles)
- [ ] Features display on map
- [ ] Can click features (popup shows)
- [ ] Layer toggles work
- [ ] "Zoom to Extent" button works
- [ ] Coordinate display shows current position
- [ ] Basemap selector works

**Issues found:**
```
(Write any issues here)
```

---

## Drawing Importer (`frontend/tools/drawing-importer.html`)

- [ ] Opens without errors
- [ ] Can select project from dropdown
- [ ] Can select DXF file
- [ ] Upload button works
- [ ] Shows progress indicator
- [ ] Shows success message after upload
- [ ] Shows error message if upload fails

**Issues found:**
```
(Write any issues here)
```

---

## Pipe Network Editor (`frontend/tools/pipe-network-editor.html`)

- [ ] Opens without errors
- [ ] Can select project
- [ ] Networks list displays
- [ ] Can view network details
- [ ] Summary cards show stats
- [ ] Pipes table displays
- [ ] Structures table displays
- [ ] Validation button works

**Issues found:**
```
(Write any issues here)
```

---

## Alignment Editor (`frontend/tools/alignment-editor.html`)

- [ ] Opens without errors
- [ ] Can select project
- [ ] Can create new alignment
- [ ] Can view alignment list
- [ ] Can edit alignment
- [ ] Can add horizontal elements
- [ ] Can add vertical elements

**Issues found:**
```
(Write any issues here)
```

---

## BMP Manager (`frontend/tools/bmp-manager.html`)

- [ ] Opens without errors
- [ ] Can select project
- [ ] BMPs list displays
- [ ] Can create new BMP
- [ ] Can view BMP details
- [ ] Can add inspection
- [ ] Can add maintenance record

**Issues found:**
```
(Write any issues here)
```

---

## Utility Coordination (`frontend/tools/utility-coordination.html`)

- [ ] Opens without errors
- [ ] Can select project
- [ ] Utilities list displays
- [ ] Can add utility
- [ ] Conflicts list displays
- [ ] Can add conflict

**Issues found:**
```
(Write any issues here)
```

---

## Sheet Set Manager (`frontend/tools/sheet-set-manager.html`)

- [ ] Opens without errors
- [ ] Can select project
- [ ] Sheet sets list displays
- [ ] Can create sheet set
- [ ] Can add sheets
- [ ] Sheet numbering works

**Issues found:**
```
(Write any issues here)
```

---

## Sheet Note Manager (`frontend/tools/sheet-note-manager.html`)

- [ ] Opens without errors
- [ ] Can select project
- [ ] Notes library displays
- [ ] Can create standard note
- [ ] Can add note to project
- [ ] Can assign note to sheet

**Issues found:**
```
(Write any issues here)
```

---

## Plot & Profile Manager (`frontend/tools/plot-profile-manager.html`)

- [ ] Opens without errors
- [ ] Can select alignment
- [ ] Profile displays
- [ ] Can adjust vertical scale
- [ ] Can export

**Issues found:**
```
(Write any issues here)
```

---

## Project Map (`frontend/tools/project-map.html`)

- [ ] Opens without errors
- [ ] Can select project
- [ ] Features load on map
- [ ] Layer controls work
- [ ] Feature popups show data
- [ ] Map zooms to project extent

**Issues found:**
```
(Write any issues here)
```

---

## Browser Compatibility

Test in different browsers:

### Chrome
- [ ] All tools work
- [ ] No console errors

### Firefox
- [ ] All tools work
- [ ] No console errors

### Edge
- [ ] All tools work
- [ ] No console errors

**Issues found:**
```
(Write any issues here)
```

---

## Summary

**Total items checked:** _____ / _____

**Critical issues:** _____

**Minor issues:** _____

**Overall status:** ⭐⭐⭐⭐⭐ (Rate 1-5 stars)

---

## Next Steps

Based on issues found, prioritize fixes:

1. **Critical issues** (prevents use):
   -

2. **High priority** (reduces functionality):
   -

3. **Low priority** (minor annoyances):
   -

---

**Testing completed by:** _____________
**Date:** _____________
