"""
Survey & Civil API Smoke Test

Runs a minimal end-to-end flow against a running API server:
- Health check
- Create/Get project
- Create survey point (GeoJSON)
- Create utility line
- Create parcel
- Create alignment, get PIs & profile
- Create a cross-section

Usage:
  1) Ensure Postgres is available (see docker/docker-compose.postgis.yml)
  2) Export environment variables or copy backend/.env.example to backend/.env
  3) Start the API server: python backend/api_server.py
  4) Run: python scripts/smoke_test_survey_civil.py
"""

import os
import sys
import time
from typing import Any, Dict
import requests

BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


def req(method: str, path: str, **kwargs) -> requests.Response:
    url = f"{BASE}{path}"
    r = requests.request(method, url, timeout=30, **kwargs)
    if not r.ok:
        try:
            detail = r.json().get("detail")
        except Exception:
            detail = r.text
        raise RuntimeError(f"{method} {path} failed: {r.status_code} {r.reason} {detail}")
    return r


def get_json(method: str, path: str, **kwargs) -> Any:
    return req(method, path, **kwargs).json()


def main() -> int:
    print("= Smoke Test: Survey & Civil API =")

    # 1) Health check
    print("- Checking health...")
    health = get_json("GET", "/api/health")
    print("  ", health)

    # 2) Create or get project
    print("- Ensuring demo project exists...")
    project_name = "Survey Civil Demo"
    projects = get_json("GET", "/api/projects")
    proj = next((p for p in projects if p.get("project_name") == project_name), None)
    if not proj:
        created = get_json("POST", "/api/projects", json={"project_name": project_name})
        project_id = created.get("project_id") or created.get("project", {}).get("project_id")
    else:
        project_id = proj["project_id"]
    print("  project_id:", project_id)

    # 3) Ensure survey point CP1 exists (idempotent)
    print("- Ensuring survey point CP1 exists...")
    existing_points = get_json("GET", f"/api/survey-points?project_id={project_id}&search=CP1")
    sp = next((p for p in existing_points if p.get("point_number") == "CP1"), None)
    if not sp:
        sp = get_json(
            "POST",
            "/api/survey-points",
            json={
                "project_id": project_id,
                "point_number": "CP1",
                "point_type": "Control",
                "geometry": {"geojson": {"type": "Point", "coordinates": [6000000, 2000000, 100]}, "srid": 2226},
            },
        )
        print("  created point:", sp)
    else:
        print("  found point:", {k: sp[k] for k in ("point_id", "point_number", "project_id") if k in sp})

    # 4) Create utility line
    print("- Creating utility line...")
    ul = get_json(
        "POST",
        "/api/utility-lines",
        json={
            "project_id": project_id,
            "utility_type": "water",
            "owner": "City",
            "status": "existing",
            "geometry": {
                "geojson": {"type": "LineString", "coordinates": [[6000000, 2000000, 100], [6000100, 2000100, 100]]},
                "srid": 2226,
            },
        },
    )
    print("  line:", ul)

    # 5) Create parcel
    print("- Creating parcel...")
    parcel = get_json(
        "POST",
        "/api/parcels",
        json={
            "project_id": project_id,
            "apn": "001-001-001",
            "owner_name": "Acme Dev",
            "situs_address": "123 Main St",
            "geometry": {
                "geojson": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [6000000, 2000000, 0],
                            [6000200, 2000000, 0],
                            [6000200, 2000200, 0],
                            [6000000, 2000200, 0],
                            [6000000, 2000000, 0],
                        ]
                    ],
                },
                "srid": 2226,
            },
        },
    )
    print("  parcel:", parcel)

    # 6) Create alignment
    print("- Creating alignment...")
    align = get_json(
        "POST",
        "/api/alignments",
        json={
            "project_id": project_id,
            "name": "Mainline",
            "srid": 2226,
            "station_start": 10.0,
            "geom": {
                "type": "LineString",
                "coordinates": [
                    [6000000, 2000000, 100],
                    [6000250, 2000000, 101],
                    [6000500, 2000100, 102],
                ],
            },
        },
    )
    alignment_id = align.get("alignment_id")
    print("  alignment_id:", alignment_id)

    # 7) Alignment PIs
    print("- Fetching PIs...")
    pis = get_json("GET", f"/api/alignments/{alignment_id}/pis")
    print("  pis count:", len(pis))

    # 8) Alignment profile
    print("- Fetching profile...")
    prof = get_json("GET", f"/api/alignments/{alignment_id}/profile")
    print("  profile elements:", len(prof.get("elements", [])))

    # 9) Create a cross-section
    print("- Creating cross-section at station 100...")
    xs = get_json(
        "POST",
        f"/api/alignments/{alignment_id}/cross-sections",
        json={
            "station": 100.0,
            "geometry": {
                "geojson": {"type": "LineString", "coordinates": [[6000100, 1999950, 98], [6000100, 2000050, 102]]},
                "srid": 2226,
            },
        },
    )
    print("  cross-section:", xs)

    # 10) Verify lists
    print("- Verifying lists...")
    sp_list = get_json("GET", f"/api/survey-points?project_id={project_id}")
    ul_list = get_json("GET", f"/api/utility-lines?project_id={project_id}")
    px_list = get_json("GET", f"/api/parcels?project_id={project_id}")
    xs_list = get_json("GET", f"/api/alignments/{alignment_id}/cross-sections")
    ok = all([
        any(p.get("point_number") == "CP1" for p in sp_list),
        len(ul_list) >= 1,
        len(px_list) >= 1,
        len(xs_list) >= 1,
    ])
    print("= RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("! Smoke test failed:", e)
        sys.exit(2)
