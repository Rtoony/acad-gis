# 🚀 ACAD=GIS Quick Start Reference

## ⚡ Start in 3 Steps

### **1. Start the Server** 
```powershell
cd "C:\Users\Josh\Desktop\ACAD_GIS\Supporting Documents"
python api_server_ENHANCED.py
```
✅ Look for: "Server running at: http://localhost:8000"
🔴 Keep this window open!

### **2. Open Dashboard**
Double-click `dashboard_MISSION_CONTROL_FINAL.html`

### **3. Check Connection**
✅ Green dot = Connected  
❌ Red dot = Server not running

---

## 🎯 Common Tasks

| Task | How To Do It |
|------|-------------|
| **Create Project** | Projects tab → New Project button → Fill form → Create |
| **Create Drawing** | Drawing Viewer tab → New Drawing button → Select project → Create |
| **Search Drawings** | Drawing Viewer tab → Type in search bar |
| **View on Map** | Drawing Viewer tab → Click any drawing card |
| **Delete Item** | Hover over card → Click trash icon → Confirm |
| **Import DXF** | Import/Export tab → Select DXF File → Upload |
| **Group by Project** | Drawing Viewer tab → Click "Group by Project" button |

---

## 🔍 Useful URLs

| What | URL |
|------|-----|
| **Dashboard** | (The HTML file you opened) |
| **API Docs** | http://localhost:8000/docs |
| **API Status** | http://localhost:8000/api/health |
| **Alt Docs** | http://localhost:8000/redoc |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Red dot (offline) | Start the server! |
| Port 8000 in use | Kill other server: `taskkill /PID <number> /F` |
| Database error | Check PostgreSQL is running |
| Button doesn't work | Open console (F12), check for errors |

---

## 🛑 Stop Everything

**Stop Server:** Press CTRL+C in the terminal  
**Close Dashboard:** Close browser tab

💾 **Your data is safe** - it's in the database!

---

## 📖 What's What?

- **Dashboard** = The HTML file (UI in browser)
- **API Server** = The Python file (must be running)
- **Database** = PostgreSQL (stores your data)
- **/docs** = Interactive API testing page
- **localhost:8000** = Your computer, port 8000

---

## 🎨 Mission Control Features

✅ Dark theme with neon glows  
✅ Animated grid background  
✅ Modal dialogs for forms  
✅ Search & filter  
✅ Group by project  
✅ Map viewer with GIS layers  
✅ Delete confirmations  
✅ File upload interface  

---

## 💡 Pro Tips

- Test API endpoints in `/docs` first
- Watch the server terminal for errors
- Use F12 in browser to see console
- Create test data to experiment safely
- Keep server terminal visible

---

**Full Guide:** See `COMPLETE_BEGINNERS_GUIDE.md`  
**Features:** See `MISSION_CONTROL_COMPLETE_GUIDE.md`

🚀 **You're all set!**
