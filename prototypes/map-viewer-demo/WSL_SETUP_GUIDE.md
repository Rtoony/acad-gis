# 🪟 Complete Setup Guide for WSL (Windows Subsystem for Linux)

**Perfect for beginners!** This guide will walk you through downloading and running the map viewer prototype on your Windows machine using WSL.

---

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ WSL installed on Windows (Ubuntu recommended)
- ✅ Git installed in WSL
- ✅ Python 3.8+ installed in WSL

### Quick Check (run these in WSL terminal):
```bash
# Check if git is installed
git --version

# Check if python is installed
python3 --version

# Check if pip is installed
pip3 --version
```

If any are missing, install them:
```bash
# Install git
sudo apt update
sudo apt install git

# Install python and pip
sudo apt install python3 python3-pip
```

---

## 📥 Method 1: Clone the Entire Repository (Recommended)

This is the easiest method if you want access to the whole project.

### Step 1: Open WSL Terminal
- Open Windows Terminal or Ubuntu app
- You'll see a command prompt like: `username@computer:~$`

### Step 2: Navigate to Where You Want the Project
```bash
# Go to your home directory
cd ~

# Or create a projects folder and go there
mkdir -p ~/projects
cd ~/projects
```

### Step 3: Clone the Repository
```bash
git clone https://github.com/Rtoony/acad-gis.git
```

This will download everything from the repository into a folder called `acad-gis`.

### Step 4: Navigate to the Prototype
```bash
cd acad-gis/prototypes/map-viewer-demo
```

### Step 5: Verify Files Are There
```bash
ls -la
```

You should see files like:
- `app.py`
- `config.json`
- `requirements.txt`
- `README.md`
- `data/` folder
- `templates/` folder
- `static/` folder

✅ **If you see these files, you're ready to move to the "Running the Application" section below!**

---

## 📥 Method 2: Download Just the Prototype Folder

If you only want the map viewer prototype without the rest of the repository.

### Step 1: Clone with Sparse Checkout

```bash
# Navigate to where you want the project
cd ~/projects

# Initialize a new git repository
mkdir map-viewer-demo
cd map-viewer-demo
git init

# Add the remote repository
git remote add origin https://github.com/Rtoony/acad-gis.git

# Enable sparse checkout
git config core.sparseCheckout true

# Specify only the prototype folder
echo "prototypes/map-viewer-demo/*" >> .git/info/sparse-checkout

# Pull the specific branch with the prototype
git pull origin claude/map-viewer-prototype-011CUUPoLMyf2X7oYfaDsdTx

# Navigate to the prototype
cd prototypes/map-viewer-demo
```

---

## 📥 Method 3: Download as ZIP (No Git Required)

If you're not comfortable with Git yet, you can download directly.

### Step 1: Download from GitHub
1. Go to: https://github.com/Rtoony/acad-gis
2. Click the green "Code" button
3. Select "Download ZIP"
4. Save the ZIP file to your Downloads folder

### Step 2: Move ZIP to WSL

In WSL, your Windows files are accessible at `/mnt/c/`

```bash
# Navigate to your Windows Downloads folder from WSL
cd /mnt/c/Users/YourWindowsUsername/Downloads

# Create a directory in WSL for projects
mkdir -p ~/projects
cd ~/projects

# Copy and extract the ZIP
cp /mnt/c/Users/YourWindowsUsername/Downloads/acad-gis-main.zip .
unzip acad-gis-main.zip

# Navigate to the prototype
cd acad-gis-main/prototypes/map-viewer-demo
```

**Note:** Replace `YourWindowsUsername` with your actual Windows username.

---

## 🚀 Running the Application

Now that you have the files locally, here's how to run the prototype:

### Step 1: Make Sure You're in the Right Directory
```bash
# You should be in the map-viewer-demo folder
pwd
# Should show something like: /home/username/projects/acad-gis/prototypes/map-viewer-demo
```

### Step 2: Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

This will install:
- Flask (the web server)
- Flask-CORS (for API access)
- Werkzeug (Flask dependency)

**What you'll see:**
```
Collecting Flask==3.0.0
Downloading flask-3.0.0-py3-none-any.whl
...
Successfully installed Flask-3.0.0 flask-cors-4.0.0 ...
```

### Step 3: Start the Flask Server
```bash
python3 app.py
```

**What you'll see:**
```
============================================================
🗺️  Interactive Leaflet Map Viewer
============================================================

Starting server at: http://localhost:5000
Data directory: /home/username/projects/acad-gis/prototypes/map-viewer-demo/data

Press CTRL+C to quit

============================================================

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

✅ **The server is now running!**

### Step 4: Open in Your Web Browser

**On Windows:**
1. Open your favorite web browser (Chrome, Firefox, Edge)
2. Go to: **http://localhost:5000**
3. The map viewer should load!

**You should see:**
- A map centered on San Francisco
- A control panel on the left
- Basemap options, data layers, styling controls, etc.

---

## 🎮 Testing the Application

Once the map loads, try these things:

### Test 1: Toggle Data Layers
1. In the left panel, click "Data Layers"
2. Check the box for "Projects"
3. You should see 15 project markers appear on the map
4. Click any marker to see project details

### Test 2: Change Basemap
1. Click "Basemap" in the left panel
2. Click "Satellite"
3. The map should switch to satellite imagery

### Test 3: Apply a Preset
1. Click "Preset Modes" in the left panel
2. Click "Executive Overview"
3. The map should change to satellite with only projects showing

### Test 4: Export the Map
1. Click "Tools" in the left panel
2. Click the "Export" button
3. Click "Export as PNG"
4. A map image should download

### Test 5: Click on Features
1. Enable the "Projects" layer
2. Click on any project marker
3. A popup should appear with details:
   - Project name
   - Cost
   - Status
   - Description
   - etc.

---

## 🛑 Stopping the Server

When you're done testing:
1. Go back to the WSL terminal
2. Press **CTRL+C** (hold Control and press C)
3. The server will stop

**You'll see:**
```
^C
Shutting down...
```

---

## 🔧 Troubleshooting

### Problem: "pip3: command not found"
**Solution:**
```bash
sudo apt update
sudo apt install python3-pip
```

### Problem: "python3: command not found"
**Solution:**
```bash
sudo apt update
sudo apt install python3
```

### Problem: "Permission denied" when installing packages
**Solution:** Use `--user` flag:
```bash
pip3 install --user -r requirements.txt
```

### Problem: Can't access localhost:5000
**Solution 1:** Check if Windows Firewall is blocking it
- Windows Security → Firewall → Allow an app
- Allow Python

**Solution 2:** Try accessing via WSL IP:
```bash
# Get your WSL IP address
hostname -I
# Use that IP in browser: http://172.x.x.x:5000
```

### Problem: Flask not found after installing
**Solution:**
```bash
# Try using python -m flask
python3 -m flask run --host=0.0.0.0 --port=5000

# Or reinstall Flask
pip3 install --upgrade --force-reinstall Flask
```

### Problem: Port 5000 already in use
**Solution:** Use a different port:
```bash
# Edit app.py last line to use port 5001
# Or run with:
python3 app.py
# Then edit app.py and change port=5000 to port=5001
```

---

## 📁 Understanding the File Structure

Once downloaded, here's what you have:

```
map-viewer-demo/
│
├── app.py                    ← The Flask server (run this!)
├── config.json              ← Map settings (center, zoom, etc.)
├── requirements.txt         ← Python packages needed
├── README.md                ← Full documentation
├── QUICKSTART.md            ← Quick reference
│
├── data/                    ← Your map data
│   ├── projects.geojson     ← 15 project markers
│   ├── service_areas.geojson ← Coverage areas
│   ├── active_sites.geojson ← Active projects
│   └── infrastructure.geojson ← Lines/routes
│
├── templates/
│   └── index.html           ← The web page
│
└── static/
    ├── css/
    │   └── styles.css       ← Styling
    └── js/
        └── app.js           ← Interactive features
```

---

## 🎨 Quick Customization

### Change the Map Center Location

Edit `config.json`:
```json
{
  "map_center": [YOUR_LATITUDE, YOUR_LONGITUDE],
  "initial_zoom": 12
}
```

For example, for New York City:
```json
{
  "map_center": [40.7128, -74.0060],
  "initial_zoom": 12
}
```

Then restart the server (CTRL+C, then `python3 app.py` again)

### Add Your Own Project Data

1. Open `data/projects.geojson` in a text editor
2. Copy the format of existing projects
3. Add your own with your coordinates
4. Save the file
5. Refresh the browser

---

## 🆘 Still Need Help?

### Common Beginner Questions

**Q: Where exactly am I in WSL?**
```bash
pwd    # Shows your current directory
ls     # Lists files in current directory
cd ~   # Go to home directory
```

**Q: How do I edit files in WSL?**
You can use:
- `nano config.json` (simple editor in terminal)
- `code config.json` (opens in VS Code if installed)
- Or edit the file in Windows (files are at `\\wsl$\Ubuntu\home\username\...`)

**Q: How do I access WSL files from Windows?**
In File Explorer, type: `\\wsl$\Ubuntu\home\username\projects\`

**Q: Can I use a Windows text editor?**
Yes! VS Code works great with WSL. Or use Notepad++ to edit files.

---

## ✅ Success Checklist

- [ ] WSL is installed and working
- [ ] Git is installed in WSL
- [ ] Python 3 is installed in WSL
- [ ] Repository is cloned/downloaded
- [ ] You're in the map-viewer-demo directory
- [ ] Dependencies are installed (`pip3 install -r requirements.txt`)
- [ ] Server starts without errors (`python3 app.py`)
- [ ] Browser loads map at localhost:5000
- [ ] You can see project markers on the map
- [ ] You can toggle layers and change basemaps

---

## 🎉 You're All Set!

If you've completed the success checklist above, you now have a fully functional interactive map viewer running locally on your machine!

**Next steps:**
1. Play around with all the features
2. Try adding your own data
3. Customize the colors and settings
4. Share your feedback!

---

**Need more help?** Check the main README.md file for detailed documentation, or feel free to ask questions!

**Happy Mapping! 🗺️**
