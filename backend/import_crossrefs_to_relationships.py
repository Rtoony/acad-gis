#!/usr/bin/env python3
"""
Import Excel -> layer_detail_relationships (flexible headers, summary).

Reads: COS_Standards_-_LAYER-TO-DETAIL_LIBRARY_CROSS-REFERENCE.xlsx

Behavior:
- Flexible header mapping for layer_name, primary/related details, etc.
- Converts detail lists to arrays.
- By default, replaces existing rows for source 'COS_CrossRef' before inserting (use --no-replace to append).
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

DEFAULT_XLSX = str((Path(__file__).resolve().parent / "COS_Standards_-_LAYER-TO-DETAIL_LIBRARY_CROSS-REFERENCE.xlsx").resolve())


def parse_args():
    p = argparse.ArgumentParser(description="Import cross-references into layer_detail_relationships")
    p.add_argument("--excel-file", default=DEFAULT_XLSX, help="Path to Excel file")
    p.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing")
    p.add_argument("--no-replace", action="store_true", help="Append without deleting existing 'COS_CrossRef' rows")
    p.add_argument("--source", default="COS_CrossRef", help="Source tag to set on imported rows")
    return p.parse_args()


def _sanitize(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def load_excel(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Excel file not found: {p}")
    return pd.read_excel(p)


def clean_crossref_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    out = df.copy()
    out.columns = [str(c) for c in out.columns]
    print(f"Columns found: {list(out.columns)}")

    norm_to_orig: Dict[str, str] = { _sanitize(c): c for c in out.columns }

    syn = {
        "layer_name": ["layer_name", "layer", "layername", "name"],
        "primary_details": ["primary_details", "primary", "primary_detail", "primary_list"],
        "related_details": ["related_details", "related", "related_detail", "related_list"],
        "critical_standard": ["critical_standard", "critical", "standard", "key_standard"],
        "callout_example": ["callout_example", "callout", "example", "calloutex"],
        "confidence": ["confidence", "weight", "score", "certainty"],
    }

    resolved: Dict[str, str] = {}
    for target, keys in syn.items():
        for key in keys:
            if key in norm_to_orig:
                resolved[target] = norm_to_orig[key]
                break

    if "layer_name" not in resolved:
        raise SystemExit("Missing required column 'Layer Name'.")

    for target, orig in resolved.items():
        out = out.rename(columns={orig: target})

    out = out.fillna("")

    # Normalize lists and numeric confidence
    def _split_list(val: object) -> List[str]:
        s = str(val).strip()
        if s == "":
            return []
        s = s.replace(";", ",")
        return [p.strip() for p in s.split(",") if p.strip()]

    for arr_col in ("primary_details", "related_details"):
        if arr_col in out.columns:
            out[arr_col] = out[arr_col].apply(_split_list)

    if "confidence" in out.columns:
        out["confidence"] = pd.to_numeric(out["confidence"], errors="coerce").fillna(1.0)

    out["layer_name"] = out["layer_name"].astype(str).str.strip()

    total_rows = len(out)
    blanks = int((out["layer_name"] == "").sum())
    to_import = len(out[out["layer_name"] != ""])
    stats = {"total_rows": int(total_rows), "blanks": int(blanks), "to_import": int(to_import)}

    out = out[out["layer_name"] != ""]
    return out, stats


def insert_crossrefs(df: pd.DataFrame, source: str) -> int:
    inserted = 0
    with database.get_db_connection() as conn:
        cur = conn.cursor()

        optional = [
            "primary_details", "related_details", "critical_standard", "callout_example", "confidence"
        ]
        available = ["layer_name"] + [c for c in optional if c in df.columns]

        cols_str = ", ".join(["relationship_id"] + available + ["source"])
        placeholders = ", ".join(["uuid_generate_v4()"] + ["%s"] * len(available) + ["%s"])
        ins_sql = f"""
            INSERT INTO layer_detail_relationships ({cols_str})
            VALUES ({placeholders})
        """

        total = len(df)
        for idx, row in df.iterrows():
            vals = []
            for c in available:
                v = row.get(c, None)
                if c in ("primary_details", "related_details"):
                    vals.append(v if isinstance(v, list) else [])
                else:
                    vals.append(v if v != "" else None)
            vals.append(source)
            cur.execute(ins_sql, tuple(vals))
            inserted += 1
            if (idx + 1) % 100 == 0:
                print(f"  Inserted {idx + 1}/{total}...")

    return inserted


def main():
    args = parse_args()
    print("=" * 70)
    print("Import Excel -> layer_detail_relationships")
    print("=" * 70)
    print(f"Excel: {args.excel_file}")

    df = load_excel(args.excel_file)
    df, stats = clean_crossref_data(df)
    print(f"Rows to import: {stats['to_import']} (blanks in layer name: {stats['blanks']})")

    if args.dry_run:
        print("Dry run only. No changes written.")
        return

    # Delete existing rows for this source unless --no-replace
    if not args.no_replace:
        database.execute_query(
            "DELETE FROM layer_detail_relationships WHERE source = %s",
            (args.source,),
            fetch=False,
        )
        print(f"Deleted existing rows for source='{args.source}'.")

    inserted = insert_crossrefs(df, source=args.source)
    print("-" * 70)
    print(f"Inserted: {inserted}")
    try:
        totals = database.execute_single(
            "SELECT COUNT(*) AS total FROM layer_detail_relationships WHERE source = %s",
            (args.source,)
        )
        print(f"Rows for source '{args.source}': {totals['total']}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
