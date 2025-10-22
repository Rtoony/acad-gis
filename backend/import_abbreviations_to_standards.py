#!/usr/bin/env python3
"""
Import Excel -> abbreviation_standards table (upsert by abbreviation).

Reads: COS_Standards_-_Abbreviations.xlsx (next to this script by default)

Features:
- Cleans and normalizes values (booleans, conflict risk).
- Upserts by abbreviation (UPDATE if exists, otherwise INSERT).
- Optional truncate mode to clear the table before import.
- Prints summary stats and progress.
"""

import sys
import argparse
from pathlib import Path
from typing import Tuple, Dict
import pandas as pd
import re

# Allow running as script from repo root or backend folder
if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))
    import database  # type: ignore
else:
    from . import database  # type: ignore

DEFAULT_XLSX = str((Path(__file__).resolve().parent / "COS_Standards_-_Abbreviations.xlsx").resolve())


def parse_args():
    p = argparse.ArgumentParser(description="Import abbreviations into abbreviation_standards")
    p.add_argument("--excel-file", default=DEFAULT_XLSX, help="Path to Excel file")
    p.add_argument("--dry-run", action="store_true", help="Load and show summary but do not write")
    p.add_argument("--truncate", action="store_true", help="Delete all rows from abbreviation_standards before import")
    return p.parse_args()


def load_excel(path: str) -> pd.DataFrame:
    f = Path(path)
    if not f.exists():
        raise SystemExit(f"Excel file not found: {f}")
    return pd.read_excel(f)


def _sanitize(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")


def clean_abbreviation_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Map varied Excel headers to our target columns and normalize values."""
    out = df.copy()
    out.columns = [str(c) for c in out.columns]

    print(f"Columns found: {list(out.columns)}")

    # Build lookup from sanitized -> original column name
    norm_to_orig: Dict[str, str] = {}
    for c in out.columns:
        norm_to_orig[_sanitize(c)] = c

    # Define synonyms (sanitized) for each target field
    synonyms = {
        "abbreviation": ["abbreviation", "abbr", "abbrv", "acronym", "short", "short_form", "shortform"],
        "full_text": [
            "full_text", "fulltext", "full_term", "fullterm", "text", "definition", "expansion", "long_text",
            "long_name", "longform", "long_form", "phrase", "meaning"
        ],
        "discipline": ["discipline", "domain", "group"],
        "category": ["category", "cat", "type", "classification"],
        "context_usage_notes": [
            "context_usage_notes", "context_notes", "usage_notes", "notes", "usage_context", "context", "usage"
        ],
        "is_ada_critical": ["is_ada_critical", "ada_critical", "ada", "is_ada", "ada_flag"],
        "conflict_risk": ["conflict_risk", "risk", "conflict", "risk_level"],
    }

    # Resolve a mapping from available columns
    resolved: Dict[str, str] = {}
    for target, keys in synonyms.items():
        for key in keys:
            if key in norm_to_orig:
                resolved[target] = norm_to_orig[key]
                break

    # Must have abbreviation and full_text
    missing_required = [t for t in ("abbreviation", "full_text") if t not in resolved]
    if missing_required:
        details = ", ".join([f"{t} via {synonyms[t]}" for t in missing_required])
        raise SystemExit(
            f"Missing required column(s). Could not find: {', '.join(missing_required)}.\n"
            f"Columns present: {list(out.columns)}\n"
            f"Looking for any of: {details}"
        )

    # Rename to target names
    for target, orig in resolved.items():
        out = out.rename(columns={orig: target})

    out = out.fillna("")

    # Normalize
    out["abbreviation"] = out["abbreviation"].astype(str).str.strip()
    out["full_text"] = out["full_text"].astype(str).str.strip()

    if "is_ada_critical" in out.columns:
        out["is_ada_critical"] = out["is_ada_critical"].apply(
            lambda x: True if str(x).strip().lower() in ("true", "yes", "y", "1") else False
        )

    if "conflict_risk" in out.columns:
        def _norm_risk(v: object) -> str:
            s = str(v).strip().capitalize()
            return s if s in ("Low", "Medium", "High") else ""
        out["conflict_risk"] = out["conflict_risk"].apply(_norm_risk)

    # Compute stats before filtering blanks
    total_rows = len(out)
    blanks = int(((out["abbreviation"] == "") | (out["full_text"] == "")).sum())
    unique_abbr = int(out[out["abbreviation"] != ""]["abbreviation"].nunique())
    duplicate_abbr = int(len(out[out["abbreviation"] != ""]) - unique_abbr)

    # Filter out rows missing required fields
    out = out[(out["abbreviation"] != "") & (out["full_text"] != "")]

    stats = {
        "total_rows": int(total_rows),
        "blanks": int(blanks),
        "unique_abbr": int(unique_abbr),
        "duplicates": int(duplicate_abbr),
        "to_import": int(len(out)),
    }

    return out, stats


def upsert_abbreviations(df: pd.DataFrame) -> tuple[int, int]:
    """Upsert by abbreviation using UPDATE then INSERT if not exists."""
    updated = 0
    inserted = 0
    with database.get_db_connection() as conn:
        cur = conn.cursor()

        # Determine available columns present in df that map to table
        optional_cols = [
            "discipline", "category", "context_usage_notes",
            "is_ada_critical", "conflict_risk"
        ]
        base_cols = ["abbreviation", "full_text"]

        available = base_cols + [c for c in optional_cols if c in df.columns]

        # Build dynamic UPDATE and INSERT statements
        set_clause = ", ".join([f"{c} = %s" for c in available if c != "abbreviation"])  # don't set key
        upd_sql = f"""
            UPDATE abbreviation_standards
            SET {set_clause}
            WHERE abbreviation = %s
        """

        # Insert without explicit primary key so DB default (e.g., SERIAL) applies
        cols_str = ", ".join(available)
        placeholders = ", ".join(["%s"] * len(available))
        ins_sql = f"""
            INSERT INTO abbreviation_standards ({cols_str})
            VALUES ({placeholders})
        """

        total = len(df)
        for idx, row in df.iterrows():
            values = [row.get(c, None) if row.get(c, None) != "" else None for c in available]
            # UPDATE first (values excluding abbreviation at SET, then key at end)
            upd_vals = [row.get(c, None) if c != "abbreviation" else None for c in available if c != "abbreviation"]
            upd_vals = [v if v != "" else None for v in upd_vals]
            upd_vals.append(row["abbreviation"])  # WHERE key
            cur.execute(upd_sql, tuple(upd_vals))
            if cur.rowcount == 0:
                cur.execute(ins_sql, tuple(values))
                inserted += 1
            else:
                updated += 1

            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{total}...")

    return updated, inserted


def main():
    args = parse_args()
    print("=" * 70)
    print("Import Excel -> abbreviation_standards")
    print("=" * 70)
    print(f"Excel: {args.excel_file}")

    df = load_excel(args.excel_file)
    df, stats = clean_abbreviation_data(df)
    print(f"Rows to import: {stats['to_import']} (unique={stats['unique_abbr']}, dupes={stats['duplicates']}, blanks={stats['blanks']})")

    if args.dry_run:
        print("Dry run only. No changes written.")
        return

    if args.truncate:
        database.execute_query("DELETE FROM abbreviation_standards", fetch=False)
        print("Truncated abbreviation_standards table.")

    updated, inserted = upsert_abbreviations(df)

    print("-" * 70)
    print(f"Updated: {updated} | Inserted: {inserted} | Total processed: {updated + inserted}")
    try:
        counts = database.execute_single(
            "SELECT COUNT(*) AS total, COUNT(*) FILTER (WHERE is_ada_critical = TRUE) AS ada FROM abbreviation_standards"
        )
        print(f"Table totals: {counts['total']} (ADA critical: {counts['ada']})")
    except Exception:
        pass


if __name__ == "__main__":
    main()
