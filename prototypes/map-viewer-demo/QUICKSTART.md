# Quick Start Guide - Map Viewer Prototype

Get up and running in 5 minutes!

## 🚀 Quick Setup

### 1. Navigate to the project
```bash
cd /home/user/acad-gis/prototypes/map-viewer-demo
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python app.py
```

### 4. Open your browser
```
http://localhost:5000
```

That's it! The map viewer should now be running.

## 🎮 Quick Tour

### First Steps

1. **Explore the Map**
   - Pan around by clicking and dragging
   - Zoom with your mouse wheel
   - The map centers on San Francisco by default

2. **Toggle Some Layers**
   - Click "Data Layers" in the left panel
   - Check "Projects" to see 15 engineering projects
   - Check "Service Areas" to see coverage zones

3. **Try a Preset**
   - Click "Preset Modes" in the left panel
   - Click "Executive Overview" for a clean presentation view
   - Try "Detailed Technical" to see all layers

4. **Change the Basemap**
   - Click "Basemap" section
   - Try "Satellite" for aerial imagery
   - Or "Grayscale" for a minimal look

5. **Click on Features**
   - Click any project marker to see details
   - Click on service area polygons
   - Click on infrastructure lines

## 🎨 Cool Things to Try

### Create Your Own View
1. Set basemap to "Light"
2. Turn on "Projects" layer only
3. Set color scheme to "Vibrant"
4. Make markers "Large"
5. Click "Save Current as Preset"

### Export a Map
1. Configure your desired view
2. Click Tools → Export
3. Choose PNG format
4. Share with your team!

### Measure on the Map
1. Click Tools → Measure
2. Use the drawing tools in top-left
3. Click points on the map
4. See distances calculated

## 📊 Sample Data Included

- **15 Engineering Projects**: Infrastructure, commercial, residential, etc.
- **3 Service Areas**: Primary, secondary, and expansion zones
- **6 Active Sites**: Current projects with status and completion %
- **8 Infrastructure Lines**: Transit, utilities, pathways

## 🎯 Common Use Cases

### Presentation Mode
1. Click "Client Presentation" preset
2. Toggle fullscreen (top-right button)
3. Present to clients

### Print a Map
1. Click "Print Ready" preset
2. Click Tools → Print
3. Use browser print dialog

### Share Your View
1. Configure your map
2. Click Tools → Share
3. Link copied to clipboard!

## ⚙️ Quick Customization

### Change Center Location
Edit `config.json`:
```json
{
  "map_center": [YOUR_LAT, YOUR_LON],
  "initial_zoom": 12
}
```

### Add Your Own Data
1. Create a GeoJSON file
2. Save it in the `data/` folder
3. Restart the server
4. It appears automatically in "Data Layers"!

## 🐛 Troubleshooting

**Map doesn't load?**
- Check that Flask server is running
- Look for errors in terminal
- Try refreshing the browser

**No data showing?**
- Make sure you checked the layer boxes
- Layers are in the "Data Layers" section
- Try clicking "Reset View"

**Can't see controls?**
- Click the hamburger menu (≡) at top
- Control panel might be collapsed
- Try refreshing the page

## 📚 Learn More

- Full documentation: See `README.md`
- API documentation: See `README.md` → API section
- Customization guide: See `README.md` → Customization section

## 🎉 You're Ready!

You now have a fully functional interactive map viewer!

**Next Steps:**
- Explore all the features
- Add your own data
- Customize colors and styles
- Share with your team

**Questions?** Check the main README.md file for detailed documentation.

---

**Happy Mapping! 🗺️**
