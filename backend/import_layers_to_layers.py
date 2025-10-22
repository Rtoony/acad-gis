#!/usr/bin/env python3
"""
Import Excel -> layers table for a chosen drawing.

- Creates a Project and Drawing if they don't exist (by name), unless --drawing-id is provided.
- Upserts layers by (drawing_id, layer_name) using database.create_layer().
- Tries to link to layer_standards automatically via name (handled in create_layer).
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd

# Allow running as script from repo root or backend folder
if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))
    import database  # type: ignore
else:
    from . import database  # type: ignore

# Default to the Excel file next to this script so it works regardless of CWD
DEFAULT_XLSX = str((Path(__file__).resolve().parent / "COS_Standards_-_Layers.xlsx").resolve())

def parse_args():
    p = argparse.ArgumentParser(description="Import Excel layers into layers table")
    p.add_argument("--excel-file", default=DEFAULT_XLSX, help="Path to Excel file")
    # Option A: use existing drawing
    p.add_argument("--drawing-id", help="Existing drawing UUID to import into")
    # Option B: or create/ensure by names
    p.add_argument("--project-name", default="COS Standards", help="Project name to create/use")
    p.add_argument("--drawing-name", default="COS Layers", help="Drawing name to create/use")
    p.add_argument("--linetype", default="CONTINUOUS", help="Default linetype")
    p.add_argument("--lineweight", type=float, default=0.25, help="Default lineweight (mm)")
    p.add_argument("--color-mode", choices=["aci", "truecolor"], default="aci",
                   help="How to store color: ACI index (default) or packed RGB truecolor")
    p.add_argument("--dry-run", action="store_true", help="Load and resolve IDs but do not write")
    p.add_argument("--truncate-drawing", action="store_true",
                   help="Delete existing layers for the target drawing before import")
    return p.parse_args()

def ensure_project_and_drawing(project_name: str, drawing_name: str) -> str:
    # Get or create project by name
    proj = database.execute_single(
        "SELECT project_id FROM projects WHERE project_name = %s",
        (project_name,)
    )
    if not proj:
        project_id = database.create_project(project_name=project_name)
    else:
        project_id = proj["project_id"]

    # Get or create drawing by name (within project)
    drw = database.execute_single(
        "SELECT drawing_id FROM drawings WHERE project_id = %s AND drawing_name = %s",
        (project_id, drawing_name)
    )
    if not drw:
        drawing_id = database.create_drawing(
            project_id=project_id,
            drawing_name=drawing_name,
            description="Imported from COS_Standards_-_Layers.xlsx"
        )
    else:
        drawing_id = drw["drawing_id"]

    return drawing_id

def load_excel(path: str) -> pd.DataFrame:
    if not Path(path).exists():
        raise SystemExit(f"Excel file not found: {path}")
    df = pd.read_excel(path)
    return df

def normalize_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    # Map common headers; we only need layer_name for the layers table.
    mapping = {
        "Layer_Name": "layer_name",
        "Layer Name": "layer_name",
        "Linetype": "linetype",
        "Lineweight": "lineweight",
        "Lineweight_mm": "lineweight",  # if present
        "Lineweight (mm)": "lineweight",
        # Color columns (any of these may be present)
        "Color": "color_raw",
        "Color Index": "color_index",
        "ACI": "aci",
        "ACI Color": "aci",
        "Color_RGB": "color_rgb",
        "Color RGB": "color_rgb",
        "Color_Name": "color_name",
        "Color Name": "color_name",
    }
    out = df.copy()
    out.columns = [str(c) for c in out.columns]
    for src, dst in mapping.items():
        if src in out.columns:
            out = out.rename(columns={src: dst})
    out = out.fillna("")
    # Keep only what we need
    keep = [
        c for c in [
            "layer_name", "linetype", "lineweight",
            "color_raw", "color_index", "aci", "color_rgb", "color_name"
        ] if c in out.columns
    ]
    if "layer_name" not in keep:
        raise SystemExit("Missing 'Layer Name' (or Layer_Name) column in Excel.")
    out = out[keep]
    # Clean types
    out["layer_name"] = out["layer_name"].astype(str).str.strip()
    if "lineweight" in out.columns:
        out["lineweight"] = pd.to_numeric(out["lineweight"], errors="coerce")
    # Stats before filtering
    total_rows = len(out)
    names = out["layer_name"]
    blank_names = int((names == "").sum())
    nonempty = names[names != ""]
    unique_nonempty = int(nonempty.nunique())
    duplicate_names = int(len(nonempty) - unique_nonempty)
    stats = {
        "total_rows": int(total_rows),
        "blank_names": int(blank_names),
        "unique_nonempty": int(unique_nonempty),
        "duplicate_names": int(duplicate_names),
    }
    return out[out["layer_name"] != ""], stats


# --- Color utilities ---

_ACI_PALETTE = {
    1: (255, 0, 0),      # Red
    2: (255, 255, 0),    # Yellow
    3: (0, 255, 0),      # Green
    4: (0, 255, 255),    # Cyan
    5: (0, 0, 255),      # Blue
    6: (255, 0, 255),    # Magenta
    7: (255, 255, 255),  # White
    8: (128, 128, 128),  # Dark Gray
    9: (192, 192, 192),  # Light Gray
}

_NAME_TO_ACI = {
    "red": 1,
    "yellow": 2,
    "green": 3,
    "cyan": 4,
    "blue": 5,
    "magenta": 6,
    "fuchsia": 6,
    "white": 7,
    "black": 7,  # AutoCAD maps 7 to white/black depending on bg
    "gray": 8,
    "grey": 8,
    "dark gray": 8,
    "light gray": 9,
}


def _to_int(val: object) -> Optional[int]:
    try:
        if val is None:
            return None
        if isinstance(val, (int,)):
            return int(val)
        s = str(val).strip()
        if s == "":
            return None
        return int(float(s))  # handle "7.0" cases
    except Exception:
        return None


def _parse_rgb(val: object) -> Optional[Tuple[int, int, int]]:
    if val is None:
        return None
    if isinstance(val, (list, tuple)) and len(val) == 3:
        try:
            r, g, b = [max(0, min(255, int(v))) for v in val]
            return (r, g, b)
        except Exception:
            return None
    s = str(val).strip()
    if s == "":
        return None
    # Accept formats like "255,0,0" or "(255, 0, 0)" or "255 0 0"
    s = s.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
    parts = [p for p in s.replace(";", ",").replace(" ", ",").split(",") if p != ""]
    if len(parts) != 3:
        return None
    try:
        r, g, b = [max(0, min(255, int(float(p)))) for p in parts]
        return (r, g, b)
    except Exception:
        return None


def _nearest_aci(rgb: Tuple[int, int, int]) -> int:
    r, g, b = rgb
    best_aci = 7
    best_dist = float("inf")
    for aci, (rr, gg, bb) in _ACI_PALETTE.items():
        d = (r - rr) ** 2 + (g - gg) ** 2 + (b - bb) ** 2
        if d < best_dist:
            best_dist = d
            best_aci = aci
    return best_aci


def _rgb_to_truecolor(rgb: Tuple[int, int, int]) -> int:
    r, g, b = rgb
    return (r << 16) | (g << 8) | b


def resolve_color(row: pd.Series, mode: str = "aci") -> Optional[int]:
    """Resolve a color integer from available columns.

    mode:
      - 'aci' (default): prefer ACI if provided; else map RGB/name to nearest ACI.
      - 'truecolor': prefer RGB packed as 0xRRGGBB; fall back to ACI if no RGB.
    """
    # Direct ACI or index
    for key in ("aci", "color_index", "color_raw"):
        if key in row:
            v = _to_int(row.get(key))
            if v is not None and 0 <= v <= 255:
                if mode == "truecolor" and v in _ACI_PALETTE:
                    # Convert ACI to approximate RGB then pack
                    return _rgb_to_truecolor(_ACI_PALETTE[v])
                return v

    # Color name
    if "color_name" in row and str(row.get("color_name") or "").strip() != "":
        name = str(row.get("color_name")).strip().lower()
        aci = _NAME_TO_ACI.get(name)
        if aci is not None:
            if mode == "truecolor":
                return _rgb_to_truecolor(_ACI_PALETTE.get(aci, (255, 255, 255)))
            return aci

    # RGB
    if "color_rgb" in row and str(row.get("color_rgb") or "").strip() != "":
        rgb = _parse_rgb(row.get("color_rgb"))
        if rgb is not None:
            if mode == "truecolor":
                return _rgb_to_truecolor(rgb)
            return _nearest_aci(rgb)

    return None

def main():
    args = parse_args()
    print("=" * 70)
    print("Import Excel -> layers table")
    print("=" * 70)
    print(f"Excel: {args.excel_file}")

    df = load_excel(args.excel_file)
    df, stats = normalize_columns(df)
    print(f"Rows to import (non-empty names): {len(df)}")
    print("-" * 70)
    print(f"Excel summary: total={stats['total_rows']} | blanks={stats['blank_names']} | "
          f"unique_names={stats['unique_nonempty']} | duplicates={stats['duplicate_names']}")

    # Resolve drawing_id
    if args.drawing_id:
        row = database.execute_single(
            "SELECT drawing_id FROM drawings WHERE drawing_id = %s",
            (args.drawing_id,)
        )
        if not row:
            raise SystemExit(f"Drawing not found: {args.drawing_id}")
        drawing_id = args.drawing_id
        print(f"Using existing drawing: {drawing_id}")
    else:
        drawing_id = ensure_project_and_drawing(args.project_name, args.drawing_name)
        print(f"Using/created drawing: {drawing_id}")

    if args.dry_run:
        print("Dry run: no rows written.")
        return

    # Optional: truncate layers for this drawing before import
    if args.truncate_drawing:
        existing = database.execute_single(
            "SELECT COUNT(*) AS c FROM layers WHERE drawing_id = %s", (drawing_id,)
        )["c"]
        database.execute_query(
            "DELETE FROM layers WHERE drawing_id = %s", (drawing_id,), fetch=False
        )
        print(f"Truncated existing layers for drawing: {existing} removed")

    # Import rows
    created = 0
    color_resolved = 0
    for idx, row in df.iterrows():
        layer_name = row.get("layer_name", "").strip()
        if not layer_name:
            continue
        linetype = row.get("linetype") or args.linetype
        lw = row.get("lineweight")
        lineweight = float(lw) if lw and not pd.isna(lw) else args.lineweight
        color_val = resolve_color(row, mode=args.color_mode)
        if color_val is not None:
            color_resolved += 1

        # We leave color=None so DB defaults apply; create_layer will try to link layer_standard_id by name.
        try:
            database.create_layer(
                drawing_id=drawing_id,
                layer_name=layer_name,
                color=color_val,
                linetype=linetype,
                lineweight=lineweight,
                is_plottable=True,
                is_locked=False,
                is_frozen=False,
                layer_standard_id=None
            )
            created += 1
            if created % 100 == 0:
                print(f"  Inserted/updated {created}...")
        except Exception as e:
            print(f"  Row {idx+1} failed ({layer_name}): {e}")

    print("-" * 70)
    print(f"Done. Inserted/updated: {created}")
    cnt = database.execute_single(
        "SELECT COUNT(*) AS c FROM layers WHERE drawing_id = %s", (drawing_id,)
    )["c"]
    print(f"Layers in this drawing now: {cnt}")
    print(f"Colors resolved: {color_resolved}/{created} (mode={args.color_mode})")
    # Post-import linkage summary (how many linked to a standard)
    try:
        link_row = database.execute_single(
            "SELECT COUNT(*) AS total, COUNT(layer_standard_id) AS linked "
            "FROM layers WHERE drawing_id = %s",
            (drawing_id,)
        )
        print(f"Linked to standards: {link_row['linked']}/{link_row['total']}")
    except Exception:
        # Table shape may vary; keep the script resilient
        pass

if __name__ == "__main__":
    main()
