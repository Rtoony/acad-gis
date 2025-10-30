# Survey & Civil API – Test Samples

Base URL: `http://localhost:8000`

Note: Replace placeholders like `<project_id>` and `<alignment_id>` with real IDs. Use `scripts/sql/seed_survey_civil_demo.sql` to seed a demo project and data.

- Health
  - `curl -s http://localhost:8000/api/health`

- Projects (demo)
  - Create: `curl -s -X POST http://localhost:8000/api/projects -H "Content-Type: application/json" -d '{"project_name":"Survey Civil Demo"}'`
  - List: `curl -s "http://localhost:8000/api/projects"`

- Survey Points
  - Create (GeoJSON):
    - `curl -s -X POST http://localhost:8000/api/survey-points -H "Content-Type: application/json" -d '{"project_id":"<project_id>","point_number":"CP1","point_type":"Control","geometry":{"geojson":{"type":"Point","coordinates":[6000000,2000000,100]},"srid":2226}}'`
  - Create (NEZ):
    - `curl -s -X POST http://localhost:8000/api/survey-points -H "Content-Type: application/json" -d '{"project_id":"<project_id>","point_number":"TP101","northing":2000050,"easting":6000050,"elevation":101.25}'`
  - List: `curl -s "http://localhost:8000/api/survey-points?project_id=<project_id>&search=CP"`
  - Import CSV (body text):
    - `curl -s -X POST http://localhost:8000/api/survey-points/import -H "Content-Type: application/json" -d @samples/survey_points_sample.json`
  - Import CSV (file upload):
    - `curl -s -F "project_id=<project_id>" -F "file=@samples/survey_points_sample.csv" http://localhost:8000/api/survey-points/import`

- Utility Lines
  - Create:
    - `curl -s -X POST http://localhost:8000/api/utility-lines -H "Content-Type: application/json" -d '{"project_id":"<project_id>","utility_type":"water","owner":"City","status":"existing","geometry":{"geojson":{"type":"LineString","coordinates":[[6000000,2000000,100],[6000100,2000100,100]]},"srid":2226}}'`
  - List: `curl -s "http://localhost:8000/api/utility-lines?project_id=<project_id>"`

- Parcels & Easements
  - Create parcel:
    - `curl -s -X POST http://localhost:8000/api/parcels -H "Content-Type: application/json" -d '{"project_id":"<project_id>","apn":"001-001-001","owner_name":"Acme Dev","situs_address":"123 Main St","geometry":{"geojson":{"type":"Polygon","coordinates":[[[6000000,2000000,0],[6000200,2000000,0],[6000200,2000200,0],[6000000,2000200,0],[6000000,2000000,0]]]},"srid":2226}}'`
  - List parcels: `curl -s "http://localhost:8000/api/parcels?project_id=<project_id>&search=Acme"`
  - Easements list: `curl -s "http://localhost:8000/api/easements?project_id=<project_id>"`

- Site Features & ROW
  - List trees: `curl -s "http://localhost:8000/api/site-trees?project_id=<project_id>"`
  - Create utility structure:
    - `curl -s -X POST http://localhost:8000/api/utility-structures -H "Content-Type: application/json" -d '{"project_id":"<project_id>","structure_type":"Valve","owner":"City","geometry":{"geojson":{"type":"Point","coordinates":[6000050,2000050,100]},"srid":2226}}'`
  - Create surface feature:
    - `curl -s -X POST http://localhost:8000/api/surface-features -H "Content-Type: application/json" -d '{"project_id":"<project_id>","feature_type":"Fence","geometry":{"geojson":{"type":"LineString","coordinates":[[6000000,2000000,0],[6000000,2000100,0]]},"srid":2226}}'`
  - Create ROW:
    - `curl -s -X POST http://localhost:8000/api/right-of-way -H "Content-Type: application/json" -d '{"project_id":"<project_id>","jurisdiction":"City","geometry":{"geojson":{"type":"Polygon","coordinates":[[[6000000,1999900,0],[6000300,1999900,0],[6000300,2000300,0],[6000000,2000300,0],[6000000,1999900,0]]]},"srid":2226}}'`

- Alignments
  - Create:
    - `curl -s -X POST http://localhost:8000/api/alignments -H "Content-Type: application/json" -d '{"project_id":"<project_id>","name":"Mainline","srid":2226,"station_start":10.0,"geom":{"type":"LineString","coordinates":[[6000000,2000000,100],[6000250,2000000,101],[6000500,2000100,102]]}}'`
  - Get: `curl -s "http://localhost:8000/api/alignments/<alignment_id>"`
  - PIs: `curl -s "http://localhost:8000/api/alignments/<alignment_id>/pis"`
  - Profile: `curl -s "http://localhost:8000/api/alignments/<alignment_id>/profile"`
  - Cross-sections list/create:
    - `curl -s "http://localhost:8000/api/alignments/<alignment_id>/cross-sections"`
    - `curl -s -X POST http://localhost:8000/api/alignments/<alignment_id>/cross-sections -H "Content-Type: application/json" -d '{"station":100.0,"geometry":{"geojson":{"type":"LineString","coordinates":[[6000100,1999950,98],[6000100,2000050,102]]},"srid":2226}}'`
  - Earthwork quantities:
    - `curl -s "http://localhost:8000/api/earthwork-quantities?alignment_id=<alignment_id>"`
  - Earthwork balance:
    - `curl -s "http://localhost:8000/api/earthwork-balance/<alignment_id>"`

- Observations & Traverse
  - Import observations:
    - `curl -s -X POST http://localhost:8000/api/observations/import -H "Content-Type: application/json" -d @samples/observations_sample.json`
  - List: `curl -s "http://localhost:8000/api/observations?project_id=<project_id>"`
  - Traverse loops: `curl -s "http://localhost:8000/api/traverse-loops?project_id=<project_id>"`

