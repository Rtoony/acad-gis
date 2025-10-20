from database import execute_query

print("First 10 symbols in database:")
symbols = execute_query(
    "SELECT block_name, domain, category FROM block_definitions ORDER BY block_name LIMIT 10"
)

for sym in symbols:
    print(f"  • {sym['block_name']:30} | {sym['domain']:15} | {sym['category']}")

print(f"\n✅ Total symbols available: {len(execute_query('SELECT * FROM block_definitions'))}")
