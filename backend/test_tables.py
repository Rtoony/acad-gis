from database import execute_query
tables = [
    'block_definitions',
    'block_attributes', 
    'block_inserts',
    'layers',
    'layer_standards',
    'projects',
    'drawings',
    'linetype_standards',
    'text_styles',
    'dimension_styles',
    'hatch_patterns',
    'construction_details'
]

print("Checking tables:")
for table in tables:
    try:
        result = execute_query(f"SELECT COUNT(*) as count FROM {table}")
        count = result[0]['count']
        print(f"✅ {table:25} | Count: {count}")
    except Exception as e:
        print(f"❌ {table:25} | Error: {e}")
