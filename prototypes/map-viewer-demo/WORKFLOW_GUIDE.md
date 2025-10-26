# 🚀 Quick Reference Guide - Map Viewer Development Workflow

This guide shows you how to work with the map viewer prototype on a daily basis.

---

## 📅 Daily Use - Starting the App

When you want to run the map viewer:

```bash
# 1. Open WSL terminal

# 2. Navigate to the prototype
cd /mnt/h/acad-gis/prototypes/map-viewer-demo

# 3. Activate virtual environment
source venv/bin/activate

# 4. Run the app
python app.py
```

**Then open browser:** http://localhost:5000

**To stop:** Press `CTRL+C` in terminal, then type `deactivate`

---

## 🔄 Getting Updates from GitHub

When new changes are pushed to GitHub and you want to update your local files:

```bash
# 1. Make sure you're in the repo root
cd /mnt/h/acad-gis

# 2. Make sure you're on the right branch
git branch
# Should show: * claude/map-viewer-prototype-011CUUPoLMyf2X7oYfaDsdTx

# 3. Get the latest changes
git pull origin claude/map-viewer-prototype-011CUUPoLMyf2X7oYfaDsdTx

# 4. If requirements.txt changed, update packages
cd prototypes/map-viewer-demo
source venv/bin/activate
pip install -r requirements.txt

# 5. Run the updated app
python app.py
```

---

## 🧪 Making Local Changes and Testing

### Option A: Just Testing (No Saving Changes)

```bash
# 1. Edit files in Windows
# Navigate to: H:\acad-gis\prototypes\map-viewer-demo
# Edit any file (app.py, config.json, data files, etc.)

# 2. Save the file

# 3. In WSL terminal:
# If app is running, press CTRL+C to stop it
# Then restart:
python app.py

# 4. Refresh browser to see changes
```

### Option B: Saving Changes to Git (When You Like Your Changes)

```bash
# 1. Check what you changed
cd /mnt/h/acad-gis
git status

# 2. See the actual changes
git diff

# 3. Add your changes
git add prototypes/map-viewer-demo/

# 4. Commit with a message
git commit -m "Description of what you changed"

# 5. Push to GitHub
git push origin claude/map-viewer-prototype-011CUUPoLMyf2X7oYfaDsdTx
```

---

## 🎨 Common Customizations to Test

### Change Map Center Location

Edit: `prototypes/map-viewer-demo/config.json`

```json
{
  "map_center": [YOUR_LAT, YOUR_LON],
  "initial_zoom": 12
}
```

Restart app to see changes.

### Add Your Own Project Data

Edit: `prototypes/map-viewer-demo/data/projects.geojson`

Add a new feature following the existing format:
```json
{
  "type": "Feature",
  "properties": {
    "name": "Your Project Name",
    "type": "infrastructure",
    "cost": "$X.XM",
    "status": "Completed",
    "description": "Your description"
  },
  "geometry": {
    "type": "Point",
    "coordinates": [LONGITUDE, LATITUDE]
  }
}
```

Refresh browser to see changes (no restart needed for data files).

### Modify Colors

Edit: `prototypes/map-viewer-demo/config.json`

Find the `color_schemes` section and modify colors:
```json
"brand": {
  "primary": "#YOUR_HEX_COLOR",
  "secondary": "#YOUR_HEX_COLOR",
  ...
}
```

Refresh browser to see changes.

---

## 🔀 Eventually Merging to Main Branch

When you're ready to integrate the prototype into your main tools:

```bash
# 1. Make sure all your changes are committed
cd /mnt/h/acad-gis
git status
# Should say "nothing to commit, working tree clean"

# 2. Switch to main branch
git checkout main

# 3. Merge the prototype branch
git merge claude/map-viewer-prototype-011CUUPoLMyf2X7oYfaDsdTx

# 4. Push to GitHub
git push origin main
```

**Note:** You might want to create a Pull Request on GitHub instead for review:
1. Go to: https://github.com/Rtoony/acad-gis
2. Click "Pull Requests" → "New Pull Request"
3. Select your branch to merge into main
4. Review changes and merge

---

## 🐛 Troubleshooting

### App Won't Start - "ModuleNotFoundError"

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt
```

### Changes Not Showing Up

```bash
# For Python/backend changes: Restart the app (CTRL+C, then python app.py)
# For HTML/CSS/JS changes: Just refresh browser (CTRL+F5 for hard refresh)
# For data files: Just refresh browser
```

### Git Says "Changes Would Be Overwritten"

```bash
# See what files changed
git status

# Option 1: Save your changes first
git add .
git commit -m "My local changes"
git pull

# Option 2: Discard local changes and get fresh copy
git checkout -- .
git pull
```

### Can't Access localhost:5000

```bash
# Make sure app is running (you should see Flask output in terminal)
# Try: http://127.0.0.1:5000 instead
# Check Windows Firewall isn't blocking Python
```

---

## 📋 Quick Command Cheatsheet

| Task | Command |
|------|---------|
| Navigate to prototype | `cd /mnt/h/acad-gis/prototypes/map-viewer-demo` |
| Activate venv | `source venv/bin/activate` |
| Run app | `python app.py` |
| Stop app | `CTRL+C` |
| Exit venv | `deactivate` |
| Check branch | `git branch` |
| Switch branch | `git checkout BRANCH_NAME` |
| Get updates | `git pull` |
| See changes | `git status` |
| Save changes | `git add . && git commit -m "message" && git push` |

---

## 🎯 Typical Daily Workflow

### Morning - Start Testing:
```bash
cd /mnt/h/acad-gis
git pull origin claude/map-viewer-prototype-011CUUPoLMyf2X7oYfaDsdTx
cd prototypes/map-viewer-demo
source venv/bin/activate
python app.py
# Open browser: localhost:5000
```

### During Day - Making Changes:
1. Edit files in Windows (H:\acad-gis\prototypes\map-viewer-demo)
2. Save files
3. Restart app (CTRL+C, then `python app.py`) or refresh browser
4. Test changes
5. Repeat

### End of Day - Save Your Work:
```bash
# In terminal (CTRL+C to stop app first)
cd /mnt/h/acad-gis
git status
git add prototypes/map-viewer-demo/
git commit -m "Describe what you changed today"
git push origin claude/map-viewer-prototype-011CUUPoLMyf2X7oYfaDsdTx
deactivate
```

---

## 📁 File Locations Reference

**WSL Path:** `/mnt/h/acad-gis/prototypes/map-viewer-demo/`

**Windows Path:** `H:\acad-gis\prototypes\map-viewer-demo\`

You can edit files using either:
- Windows apps (VS Code, Notepad++, etc.) - Use `H:\` path
- WSL text editors (nano, vim) - Use `/mnt/h/` path

Both point to the same files!

---

## ✅ Daily Checklist

Before you start coding:
- [ ] Open WSL terminal
- [ ] `cd /mnt/h/acad-gis`
- [ ] `git pull` (get latest changes)
- [ ] `cd prototypes/map-viewer-demo`
- [ ] `source venv/bin/activate`
- [ ] `python app.py`
- [ ] Browser open to localhost:5000

Before you finish for the day:
- [ ] Stop app (CTRL+C)
- [ ] `git status` (check what changed)
- [ ] `git add` and `git commit` (save changes)
- [ ] `git push` (upload to GitHub)
- [ ] `deactivate` (exit venv)

---

## 🆘 Need Help?

- Check `README.md` for full documentation
- Check `WSL_SETUP_GUIDE.md` for setup issues
- Check `QUICKSTART.md` for feature overview

---

**Save this guide!** Print it or keep it handy while you work. 😊
