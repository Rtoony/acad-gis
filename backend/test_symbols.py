import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))
    from database import execute_query  # type: ignore
else:
    from .database import execute_query  # type: ignore

print("First 10 symbols in database:")
symbols = execute_query(
    "SELECT block_name, domain, category FROM block_definitions ORDER BY block_name LIMIT 10"
)

for sym in symbols:
    print(f"  • {sym['block_name']:30} | {sym['domain']:15} | {sym['category']}")

print(f"\n✅ Total symbols available: {len(execute_query('SELECT * FROM block_definitions'))}")
