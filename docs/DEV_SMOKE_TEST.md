Dev Smoke Test for Survey & Civil

Prereqs
- Docker Desktop (for local PostGIS) or an accessible Postgres/PostGIS.
- Python env with backend deps: `pip install -r backend/requirements.txt`.

One-command bring-up (Windows/PowerShell)
- `pwsh -File scripts/dev_up.ps1`
- Does: docker up PostGIS -> venv + deps -> migrations -> start API -> run smoke test.

Start PostGIS (Option A: Docker)
- `docker compose -f docker/docker-compose.postgis.yml up -d`
- This exposes Postgres on `localhost:5432` with DB `acadgis`, user/pass `postgres/postgres`.

Configure backend/.env
- Copy `backend/.env.example` to `backend/.env` (edit if needed).

Apply migrations
- `python backend/run_migrations.py`

Seed (optional)
- `psql -h localhost -U postgres -d acadgis -f scripts/sql/seed_survey_civil_demo.sql`

Run API
- `python backend/api_server.py`

Run smoke test
- `python scripts/smoke_test_survey_civil.py`
- Expected output ends with `= RESULT: PASS`.

Manual checks (optional)
- cURL samples in `docs/API_TEST_SAMPLES.md`
- VSCode/JetBrains `.http`: `scripts/http/survey_civil.http`
- Postman: import `docs/postman/SurveyCivil.postman_collection.json`
