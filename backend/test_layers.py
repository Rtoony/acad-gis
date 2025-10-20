from database import execute_query

print("First 10 layer standards:")
layers = execute_query(
    "SELECT layer_name, description FROM layer_standards ORDER BY layer_name LIMIT 10"
)

for layer in layers:
    desc = layer['description'][:50] if layer['description'] else "No description"
    print(f"  • {layer['layer_name']:20} | {desc}")

print(f"\n✅ Total layer standards: {len(execute_query('SELECT * FROM layer_standards'))}")
