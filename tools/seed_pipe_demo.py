"""
Seed sample data for pipe networks, structures, utilities, conflicts, and notes.

Usage:
  python tools/seed_pipe_demo.py

Notes:
- Reads DB credentials from backend/.env (preferred) or .env
- Idempotent per project/network: reuses projects and networks by name,
  then clears only the network's pipes/structures before reseeding.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

from dotenv import load_dotenv
import psycopg2
import re


# Prefer backend/.env to match the backend service
for env_path in (Path('backend/.env'), Path('.env')):
    if env_path.exists():
        load_dotenv(env_path)
        break

# Ensure we can import backend/database.py
import sys
sys.path.insert(0, str(Path('backend').resolve()))
import database  # type: ignore


def get_or_create_project(project_name: str,
                          project_number: Optional[str] = None,
                          client_name: Optional[str] = None,
                          description: Optional[str] = None) -> str:
    row = database.execute_single(
        "SELECT project_id FROM projects WHERE project_name = %s",
        (project_name,)
    )
    if row:
        return row['project_id']
    return database.create_project(
        project_name=project_name,
        project_number=project_number,
        client_name=client_name,
        description=description,
        metadata={"seed": "demo-v1"}
    )


def get_or_create_network(project_id: str, name: str, description: Optional[str]) -> str:
    row = database.execute_single(
        "SELECT network_id FROM pipe_networks WHERE project_id = %s AND name = %s",
        (project_id, name)
    )
    if row:
        return row['network_id']
    return database.create_pipe_network(project_id=project_id, name=name, description=description)


def clear_network_content(network_id: str) -> None:
    # Only delete pipes/structures for this network to keep project-level items intact
    database.execute_query("DELETE FROM pipes WHERE network_id = %s", (network_id,), fetch=False)
    database.execute_query("DELETE FROM structures WHERE network_id = %s", (network_id,), fetch=False)


def ensure_utility(project_id: str, company: str, utility_type: str,
                   status: str = 'requested',
                   contact: Optional[str] = None) -> str:
    row = database.execute_single(
        "SELECT utility_id FROM utilities WHERE project_id = %s AND company = %s",
        (project_id, company)
    )
    if row:
        return row['utility_id']
    return database.create_utility(
        project_id=project_id,
        company=company,
        utility_type=utility_type,
        status=status,
        request_date=None,
        response_date=None,
        contact=contact,
        metadata={"seed": "demo-v1"}
    )


def ensure_note(project_id: str, title: str, category: str, text: str,
                tags: Optional[List[str]] = None, is_standard: bool = True) -> None:
    # Upsert-like behavior based on (project_id, title)
    existing = database.execute_single(
        "SELECT note_id FROM sheet_notes WHERE project_id = %s AND title = %s",
        (project_id, title)
    )
    if existing:
        database.execute_query(
            """
            UPDATE sheet_notes
            SET category = %s, text = %s, tags = %s, is_standard = %s, updated_at = CURRENT_TIMESTAMP
            WHERE note_id = %s
            """,
            (category, text, (tags or []), is_standard, existing['note_id']),
            fetch=False
        )
    else:
        database.execute_query(
            """
            INSERT INTO sheet_notes (project_id, title, category, text, tags, is_standard)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (project_id, title, category, text, (tags or []), is_standard),
            fetch=False
        )


def seed_structures(network_id: str, points: Dict[str, Tuple[float, float]]
                   ) -> Dict[str, str]:
    """Create structures using allowed `type` values discovered from the DB.

    - If `structures.type` is an enum, we use the enum labels.
    - Else, we parse CHECK constraints to extract the allowed set.
    - We then map shorthands (MH/CB) to the closest allowed value.
    """

    def normalize(s: str) -> str:
        return re.sub(r"[^a-z0-9]", "", s.lower())

    # Probe allowed types: enum labels or CHECK constraint list
    def discover_allowed_types() -> List[str]:
        # Try enum
        enum_rows = database.execute_query(
            """
            SELECT e.enumlabel
            FROM information_schema.columns c
            JOIN pg_type t ON c.udt_name = t.typname
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE c.table_name = 'structures' AND c.column_name = 'type'
            ORDER BY e.enumsortorder
            """
        )
        if enum_rows:
            return [r['enumlabel'] for r in enum_rows]

        # Try CHECK constraints
        cons = database.execute_query(
            """
            SELECT pg_get_constraintdef(c.oid) AS def
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            WHERE t.relname = 'structures' AND c.contype = 'c'
            """
        )
        candidates: Set[str] = set()
        for row in cons:
            d = row.get('def') or ''
            # Grab all single-quoted strings; typical defs include ARRAY['A','B',...]
            for m in re.finditer(r"'([^']*)'", d):
                candidates.add(m.group(1))
        return sorted(candidates) if candidates else []

    allowed = discover_allowed_types()
    if allowed:
        print(f"  structures.type options: {allowed}")

    # Synonym pools for mapping shorthands to allowed labels
    synonyms = {
        'MH': ['MANHOLE', 'Manhole', 'MH', 'JUNCTION', 'NODE'],
        'CB': ['CATCH_BASIN', 'Catch Basin', 'INLET', 'CB', 'CURB INLET', 'DROP INLET'],
    }

    def pick_label(shorthand: str) -> List[str]:
        # If we don't know allowed values, fall back to synonym list
        if not allowed:
            return synonyms.get(shorthand, [shorthand])
        norm_allowed = {normalize(v): v for v in allowed}
        for cand in synonyms.get(shorthand, [shorthand]):
            key = normalize(cand)
            if key in norm_allowed:
                return [norm_allowed[key]]
        # No synonym found; use first allowed as a reasonable default
        return [allowed[0]]
    ids: Dict[str, str] = {}
    for key, (lon, lat) in points.items():
        shorthand = 'MH' if key.startswith('S') else 'CB'
        candidates = pick_label(shorthand)

        last_err: Optional[Exception] = None
        for candidate in candidates:
            try:
                structure_id = database.create_structure(
                    project_id=None,  # derive from network
                    network_id=network_id,
                    structure_type=candidate,
                    rim_elev=100.0,
                    sump_depth=1.2,
                    geom={
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    srid=4326,
                    metadata={"seed": "demo-v1", "label": key}
                )
                ids[key] = structure_id
                break
            except psycopg2.errors.CheckViolation as e:  # type: ignore[attr-defined]
                last_err = e
                continue
            except Exception as e:
                last_err = e
                continue
        else:
            # Exhausted candidates
            raise RuntimeError(
                f"Failed to insert structure '{key}' at {lon},{lat}. "
                f"Tried candidates {candidates}. Last error: {last_err}"
            )
    return ids


def seed_pipes(network_id: str,
               segments: List[Dict[str, object]],
               struct_ids: Dict[str, str]) -> None:
    for seg in segments:
        up = struct_ids[seg['up']]  # type: ignore[index]
        dn = struct_ids[seg['dn']]  # type: ignore[index]
        coords = seg['coords']  # type: ignore[assignment]
        length_m = float(seg.get('length_m', 60.0))  # default
        slope = float(seg.get('slope')) if seg.get('slope') is not None else None
        inv_up = float(seg.get('invert_up', 100.0))
        inv_dn = float(seg.get('invert_dn', inv_up - (slope or 0.0) * length_m))

        database.create_pipe(
            network_id=network_id,
            up_structure_id=up,
            down_structure_id=dn,
            diameter_mm=float(seg.get('diameter_mm', 300)),
            material=str(seg.get('material', 'PVC')),
            slope=slope,
            length_m=length_m,
            invert_up=inv_up,
            invert_dn=inv_dn,
            status=str(seg.get('status', 'proposed')),
            geom={
                "type": "LineString",
                "coordinates": coords,  # type: ignore[arg-type]
            },
            srid=4326,
            metadata={"seed": "demo-v1"}
        )


def seed_conflict(project_id: str, utility_id: str, lon: float, lat: float,
                  description: str, severity: int = 2) -> None:
    database.create_conflict_record({
        'project_id': project_id,
        'utility_id': utility_id,
        'description': description,
        'severity': severity,
        'resolved': False,
        'suggestions': 'Adjust alignment or lower pipe to provide clearance.',
        'location': {
            'type': 'Point',
            'coordinates': [lon, lat]
        },
        'srid': 4326
    })


def seed_project_mission_creek() -> None:
    project_id = get_or_create_project(
        project_name='Mission Creek Phase 1',
        project_number='MC-001',
        client_name='City of Mission',
        description='Storm sewer improvements along North Basin.'
    )

    network_id = get_or_create_network(
        project_id, 'North Basin Storm (original)', 'Baseline storm layout with mixed slopes.'
    )
    clear_network_content(network_id)

    points = {
        'S1': (-122.4060, 37.7840),
        'S2': (-122.4055, 37.7838),
        'S3': (-122.4050, 37.7836),
    }
    struct_ids = seed_structures(network_id, points)

    pipes = [
        {
            'up': 'S1', 'dn': 'S2',
            'diameter_mm': 300,  # 12 in → required ~0.0033
            'material': 'RCP',
            'slope': 0.0030,  # slightly below
            'length_m': 60.0,
            'invert_up': 100.0,
            'coords': [points['S1'], points['S2']],
        },
        {
            'up': 'S2', 'dn': 'S3',
            'diameter_mm': 300,
            'material': 'RCP',
            'slope': 0.0060,  # above
            'length_m': 55.0,
            'invert_up': 99.82,
            'coords': [points['S2'], points['S3']],
        },
        {
            'up': 'S1', 'dn': 'S3',
            'diameter_mm': 250,  # ~10 in → required ~0.0028
            'material': 'PVC',
            'slope': 0.0020,  # below
            'length_m': 85.0,
            'invert_up': 100.2,
            'coords': [points['S1'], points['S3']],
            'status': 'alternate'
        },
    ]
    seed_pipes(network_id, pipes, struct_ids)

    # Utilities and conflicts
    util = ensure_utility(project_id, 'Mission Creek Water', 'Water', status='active')
    seed_conflict(project_id, util, lon=-122.4057, lat=37.7839,
                  description='Potential conflict with existing 12" water main.', severity=2)

    # Notes
    ensure_note(project_id, 'Storm Pipe Installation', 'Storm',
                'Install per City of Mission standards. Compact bedding to 95% ASTM D698.',
                tags=['storm', 'installation'])
    ensure_note(project_id, 'Trench Safety', 'General',
                'Contractor to follow OSHA trenching and excavation standards.',
                tags=['safety', 'trench'])


def seed_project_ridgeview() -> None:
    project_id = get_or_create_project(
        project_name='Ridgeview Logistics Park',
        project_number='RV-100',
        client_name='Ridgeview Development Co.',
        description='Industrial park utilities and drainage.'
    )

    # Storm Phase A
    storm_id = get_or_create_network(project_id, 'Ridgeview Storm Phase A', 'Phase A storm sewers')
    clear_network_content(storm_id)
    pts_storm = {
        'S1': (-122.2100, 37.7500),
        'S2': (-122.2096, 37.7497),
        'S3': (-122.2092, 37.7494),
        'S4': (-122.2088, 37.7491),
    }
    sids_storm = seed_structures(storm_id, pts_storm)
    pipes_storm = [
        {'up': 'S1', 'dn': 'S2', 'diameter_mm': 450, 'material': 'RCP', 'slope': 0.0015, 'length_m': 45.0,
         'invert_up': 101.0, 'coords': [pts_storm['S1'], pts_storm['S2']]},  # below (18" → 0.0019)
        {'up': 'S2', 'dn': 'S3', 'diameter_mm': 450, 'material': 'RCP', 'slope': 0.0030, 'length_m': 50.0,
         'invert_up': 100.93, 'coords': [pts_storm['S2'], pts_storm['S3']]},  # above
        {'up': 'S3', 'dn': 'S4', 'diameter_mm': 375, 'material': 'PVC', 'slope': 0.0025, 'length_m': 40.0,
         'invert_up': 100.78, 'coords': [pts_storm['S3'], pts_storm['S4']]},
    ]
    seed_pipes(storm_id, pipes_storm, sids_storm)

    # Sanitary Trunk
    san_id = get_or_create_network(project_id, 'Ridgeview Sanitary Trunk', 'Main sanitary trunk line')
    clear_network_content(san_id)
    pts_san = {
        'S1': (-122.2110, 37.7505),
        'S2': (-122.2106, 37.7502),
        'S3': (-122.2102, 37.7499),
    }
    sids_san = seed_structures(san_id, pts_san)
    pipes_san = [
        {'up': 'S1', 'dn': 'S2', 'diameter_mm': 200, 'material': 'PVC', 'slope': 0.0050, 'length_m': 55.0,
         'invert_up': 102.0, 'coords': [pts_san['S1'], pts_san['S2']]},  # above (8" → 0.0040)
        {'up': 'S2', 'dn': 'S3', 'diameter_mm': 200, 'material': 'PVC', 'slope': 0.0030, 'length_m': 50.0,
         'invert_up': 101.73, 'coords': [pts_san['S2'], pts_san['S3']]},  # below
    ]
    seed_pipes(san_id, pipes_san, sids_san)

    util = ensure_utility(project_id, 'Ridgeview Power', 'Electric', status='active')
    seed_conflict(project_id, util, lon=-122.2098, lat=37.7496,
                  description='Crossing with primary power ductbank.', severity=3)

    ensure_note(project_id, 'Sanitary Trunk Bedding', 'Sanitary',
                'Provide granular bedding and initial backfill to springline.',
                tags=['sanitary', 'bedding'])


def seed_project_harborview() -> None:
    project_id = get_or_create_project(
        project_name='Harborview Redevelopment',
        project_number='HB-042',
        client_name='Harborview Partners',
        description='Storm retrofit with biocell connection.'
    )

    network_id = get_or_create_network(project_id, 'Harborview Storm Retrofit', 'Retrofit ties into existing biocell')
    clear_network_content(network_id)

    points = {
        'S1': (-122.3350, 37.8100),
        'S2': (-122.3346, 37.8097),
    }
    struct_ids = seed_structures(network_id, points)

    pipes = [
        {'up': 'S1', 'dn': 'S2', 'diameter_mm': 300, 'material': 'HDPE', 'slope': 0.0040, 'length_m': 42.0,
         'invert_up': 99.0, 'coords': [points['S1'], points['S2']]},  # above
        {'up': 'S2', 'dn': 'S1', 'diameter_mm': 300, 'material': 'HDPE', 'slope': 0.0020, 'length_m': 42.0,
         'invert_up': 98.83, 'coords': [points['S2'], points['S1']], 'status': 'alternate'},  # below
    ]
    seed_pipes(network_id, pipes, struct_ids)

    util = ensure_utility(project_id, 'Harborview Gas', 'Gas', status='active')
    seed_conflict(project_id, util, lon=-122.3348, lat=37.8098,
                  description='Gas service near proposed storm lead.', severity=1)

    ensure_note(project_id, 'Biocell Connection Detail', 'Storm',
                'Tie-in at biocell forebay per standard detail ST-302.',
                tags=['storm', 'biocell'])


def main() -> None:
    print('Seeding demo data (demo-v1)...')
    # Quick connectivity check
    with database.get_db_connection():
        pass

    seed_project_mission_creek()
    seed_project_ridgeview()
    seed_project_harborview()

    print('\nSummary:')
    networks = database.list_pipe_networks()
    print(f"  Pipe networks: {len(networks)}")
    for n in networks:
        name = n.get('name')
        proj = n.get('project_name')
        pc = n.get('pipe_count') or 0
        pbm = n.get('pipes_below_min') or 0
        avg = n.get('avg_slope')
        worst = n.get('worst_margin')
        avg_txt = f"{avg*100:.2f}%" if avg is not None else '-'
        worst_txt = f"{worst*100:.2f}%" if worst is not None else '-'
        print(f"    - {proj} / {name}: pipes={pc}, below_min={pbm}, avg_slope={avg_txt}, worst_margin={worst_txt}")

    print('\nDone. You can now:')
    print('  - Open tool_launcher.html → Pipe Network Editor')
    print('  - Run: streamlit run tools/pipe_network_viewer.py')


if __name__ == '__main__':
    main()
