# ACAD=GIS
# Create all the folders
mkdir -p backend frontend/tools frontend/shared docs database/migrations scripts tests archive

# Create a better README
cat > README.md << 'EOF'
# ACAD=GIS

GIS-enabled CAD drawing management system with modular mini-tools.

## Project Status
🚧 Currently restructuring from monolithic dashboard to modular architecture

## Tech Stack
- **Backend:** Python Flask API
- **Frontend:** React (CDN), Leaflet maps
- **Database:** PostgreSQL/PostGIS (Supabase)
- **Development:** WSL, VS Code, Claude Code

## Project Structure
```
acad-gis/
├── backend/           # Flask API server
├── frontend/
│   ├── tools/        # Individual mini-tools (HTML)
│   └── shared/       # Shared CSS, JS, components
├── docs/             # Documentation
├── database/         # Schema and migrations
└── scripts/          # Utility scripts
```

## Quick Start
Coming soon...
