#!/usr/bin/env python3
"""
Import Excel -> detail_standards table (flexible headers, summary, optional truncate).

Reads: COS_Standards_-_Details.xlsx (next to this script by default)

Behavior:
- Flexible header mapping (Detail Number/Title, Description, etc.).
- Cleans arrays for Related Blocks/Layers.
- Inserts rows with generated UUIDs (uuid_generate_v4()).
- Optional --truncate to clear table first (recommended to avoid duplicates).
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Tuple, List
import re
import pandas as pd

# Allow running as script from repo root or backend folder
if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))
    import database  # type: ignore
else:
    from . import database  # type: ignore

DEFAULT_XLSX = str((Path(__file__).resolve().parent / "COS_Standards_-_Details.xlsx").resolve())


def parse_args():
    p = argparse.ArgumentParser(description="Import details into detail_standards")
    p.add_argument("--excel-file", default=DEFAULT_XLSX, help="Path to Excel file")
    p.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing")
    p.add_argument("--truncate", action="store_true", help="Delete all from detail_standards before import")
    return p.parse_args()


def _sanitize(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def load_excel(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Excel file not found: {p}")
    return pd.read_excel(p)


def clean_detail_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    out = df.copy()
    out.columns = [str(c) for c in out.columns]
    print(f"Columns found: {list(out.columns)}")

    norm_to_orig: Dict[str, str] = { _sanitize(c): c for c in out.columns }

    syn = {
        "detail_number": ["detail_number", "number", "detail_no", "detailnum", "id", "detail_id"],
        "detail_title": ["detail_title", "title", "name", "detailname"],
        "description": ["description", "detail_description", "desc", "notes"],
        "usage_context": ["usage_context", "usage", "context"],
        "discipline": ["discipline", "domain", "group"],
        "category": ["category", "type", "classification"],
        "csi_section": ["csi_section", "csi", "csi_code", "csi_division"],
        "related_blocks": ["related_blocks", "blocks", "relatedsymbols", "related_blocks_list"],
        "related_layers": ["related_layers", "layers", "relatedlayers", "related_layers_list"],
        "ada_standard": ["ada_standard", "ada", "ada_code"],
        "cbc_standard": ["cbc_standard", "cbc", "cbc_code"],
    }

    resolved: Dict[str, str] = {}
    for target, keys in syn.items():
        for key in keys:
            if key in norm_to_orig:
                resolved[target] = norm_to_orig[key]
                break

    # Require a title at minimum
    if "detail_title" not in resolved:
        raise SystemExit(
            "Missing required column 'Detail Title' (any of: Detail Title, Title, Name)."
        )

    # Rename
    for target, orig in resolved.items():
        out = out.rename(columns={orig: target})

    out = out.fillna("")

    # Normalize
    out["detail_title"] = out["detail_title"].astype(str).str.strip()
    if "detail_number" in out.columns:
        out["detail_number"] = out["detail_number"].astype(str).str.strip()

    # Arrays
    def _split_list(val: object) -> List[str]:
        s = str(val).strip()
        if s == "":
            return []
        s = s.replace(";", ",")
        parts = [p.strip() for p in s.split(",") if p.strip()]
        return parts

    for arr_col in ("related_blocks", "related_layers"):
        if arr_col in out.columns:
            out[arr_col] = out[arr_col].apply(_split_list)

    total_rows = len(out)
    blanks = int((out["detail_title"] == "").sum())
    to_import = len(out[out["detail_title"] != ""])
    stats = {"total_rows": int(total_rows), "blanks": int(blanks), "to_import": int(to_import)}

    out = out[out["detail_title"] != ""]
    return out, stats


def insert_details(df: pd.DataFrame) -> int:
    inserted = 0
    with database.get_db_connection() as conn:
        cur = conn.cursor()

        optional = [
            "detail_number", "usage_context", "discipline", "category",
            "csi_section", "related_blocks", "related_layers", "ada_standard", "cbc_standard"
        ]
        available = ["detail_title"]
        if "description" in df.columns:
            available.append("description")
        else:
            # Ensure description exists (NULL) to satisfy NOT NULL if applicable
            df = df.assign(description="")
            available.append("description")
        for c in optional:
            if c in df.columns:
                available.append(c)

        cols_str = ", ".join(["detail_id"] + available)
        placeholders = ", ".join(["uuid_generate_v4()"] + ["%s"] * len(available))
        ins_sql = f"""
            INSERT INTO detail_standards ({cols_str})
            VALUES ({placeholders})
        """

        total = len(df)
        for idx, row in df.iterrows():
            vals = []
            for c in available:
                v = row.get(c, None)
                if c in ("related_blocks", "related_layers"):
                    vals.append(v if isinstance(v, list) else [])
                else:
                    vals.append(v if v != "" else None)
            cur.execute(ins_sql, tuple(vals))
            inserted += 1
            if (idx + 1) % 100 == 0:
                print(f"  Inserted {idx + 1}/{total}...")

    return inserted


def main():
    args = parse_args()
    print("=" * 70)
    print("Import Excel -> detail_standards")
    print("=" * 70)
    print(f"Excel: {args.excel_file}")

    df = load_excel(args.excel_file)
    df, stats = clean_detail_data(df)
    print(f"Rows to import: {stats['to_import']} (blanks in title: {stats['blanks']})")

    if args.dry_run:
        print("Dry run only. No changes written.")
        return

    if args.truncate:
        database.execute_query("DELETE FROM detail_standards", fetch=False)
        print("Truncated detail_standards table.")

    inserted = insert_details(df)
    print("-" * 70)
    print(f"Inserted: {inserted}")
    try:
        totals = database.execute_single("SELECT COUNT(*) AS total FROM detail_standards")
        print(f"Table total: {totals['total']}")
    except Exception:
        pass


if __name__ == "__main__":
    main()

