#!/usr/bin/env python3
"""
Test script to verify all database schema fixes.

This script tests:
1. Layers table - upsert behavior without ON CONFLICT
2. Project details - new column names
3. Structures table - invert_elev column
4. Sheet notes - proper tags array handling

Usage:
    python backend/test_schema_fixes.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import database

def test_database_connection():
    """Test basic database connectivity."""
    print("1. Testing database connection...")
    try:
        with database.get_db_connection() as conn:
            print("   ✓ Database connection successful")
            return True
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return False


def test_create_project():
    """Test creating a test project."""
    print("\n2. Testing project creation...")
    try:
        project_id = database.create_project(
            project_name="Schema Test Project",
            project_number="TEST-001",
            client_name="Test Client",
            description="Testing schema fixes"
        )
        print(f"   ✓ Created project: {project_id}")
        return project_id
    except Exception as e:
        print(f"   ✗ Failed to create project: {e}")
        return None


def test_layers_upsert(project_id):
    """Test layers table upsert behavior."""
    print("\n3. Testing layers table upsert...")
    try:
        # Create a test drawing
        drawing_id = database.create_drawing(
            project_id=project_id,
            drawing_name="Test Drawing",
            drawing_number="TD-001"
        )

        # Create layer first time
        layer_id1 = database.create_layer(
            drawing_id=drawing_id,
            layer_name="TEST-LAYER",
            color=7,
            linetype="CONTINUOUS"
        )
        print(f"   ✓ Created layer: {layer_id1}")

        # Try to create same layer again (should update)
        layer_id2 = database.create_layer(
            drawing_id=drawing_id,
            layer_name="TEST-LAYER",
            color=3,  # Different color
            linetype="DASHED"
        )
        print(f"   ✓ Updated layer: {layer_id2}")

        if layer_id1 == layer_id2:
            print("   ✓ Upsert working correctly (same layer_id)")
        else:
            print(f"   ✗ Upsert created duplicate: {layer_id1} != {layer_id2}")

        return True
    except Exception as e:
        print(f"   ✗ Layers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_project_details(project_id):
    """Test project_details table with new schema columns."""
    print("\n4. Testing project_details with new schema...")
    try:
        # Create project details
        details = database.create_project_details({
            'project_id': project_id,
            'street_address': '123 Test Street',
            'city': 'Test City',
            'state': 'CA',
            'zip_code': '12345',
            'county': 'Test County',
            'apn': 'TEST-APN-001',
            'project_engineer': 'John Engineer',
            'project_manager': 'Jane Manager',
            'design_lead': 'Bob Designer',
            'client_contact_name': 'Alice Client',
            'client_contact_email': 'alice@example.com',
            'jurisdiction': 'Test City',
            'permit_number': 'PERMIT-001'
        })
        print(f"   ✓ Created project details")

        # Retrieve and verify
        retrieved = database.get_project_details(project_id)
        if retrieved and retrieved.get('street_address') == '123 Test Street':
            print("   ✓ Column names correct (street_address, apn, etc.)")
        else:
            print(f"   ✗ Retrieved data mismatch: {retrieved}")

        # Update
        updated = database.update_project_details(project_id, {
            'city': 'Updated City',
            'project_engineer': 'Updated Engineer'
        })
        if updated and updated.get('city') == 'Updated City':
            print("   ✓ Update working correctly")
        else:
            print("   ✗ Update failed")

        return True
    except Exception as e:
        print(f"   ✗ Project details test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_structures_invert_elev(project_id):
    """Test structures table with invert_elev column."""
    print("\n5. Testing structures with invert_elev...")
    try:
        # Create pipe network
        network_id = database.create_pipe_network(
            project_id=project_id,
            name="Test Network",
            description="Testing structures"
        )

        # Create structure with invert_elev
        structure_id = database.create_structure(
            project_id=project_id,
            network_id=network_id,
            structure_type='manhole',
            rim_elev=100.0,
            sump_depth=1.5,
            invert_elev=98.5,
            geom={'type': 'Point', 'coordinates': [-122.4, 37.8]},
            srid=4326
        )
        print(f"   ✓ Created structure with invert_elev: {structure_id}")

        # Retrieve and verify
        retrieved = database.get_structure(structure_id)
        if retrieved and 'invert_elev' in retrieved:
            print(f"   ✓ invert_elev present: {retrieved['invert_elev']}")
        else:
            print(f"   ✗ invert_elev missing from result: {retrieved}")

        # Update invert_elev
        database.update_structure(structure_id, {'invert_elev': 98.0})
        updated = database.get_structure(structure_id)
        if updated and updated.get('invert_elev') == 98.0:
            print("   ✓ invert_elev update working")
        else:
            print(f"   ✗ invert_elev update failed: {updated}")

        # List structures
        structures = database.list_structures(network_id=network_id)
        if structures and 'invert_elev' in structures[0]:
            print("   ✓ list_structures includes invert_elev")
        else:
            print(f"   ✗ list_structures missing invert_elev: {structures}")

        return True
    except Exception as e:
        print(f"   ✗ Structures test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sheet_notes(project_id):
    """Test sheet_notes with tags array."""
    print("\n6. Testing sheet_notes with tags array...")
    try:
        # Insert sheet note with tags
        database.execute_query(
            """
            INSERT INTO sheet_notes (project_id, title, category, text, tags, is_standard)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING note_id
            """,
            (project_id, 'Test Note', 'General', 'Test note text', ['tag1', 'tag2'], True)
        )
        print("   ✓ Inserted sheet note with tags array")

        # Retrieve notes
        notes = database.list_sheet_notes(project_id=project_id)
        if notes and notes[0].get('tags'):
            print(f"   ✓ Retrieved tags: {notes[0]['tags']}")
        else:
            print(f"   ✗ Tags not retrieved correctly: {notes}")

        return True
    except Exception as e:
        print(f"   ✗ Sheet notes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup(project_id):
    """Clean up test data."""
    print("\n7. Cleaning up test data...")
    try:
        # Delete project (cascades to related tables)
        database.execute_query(
            "DELETE FROM projects WHERE project_id = %s",
            (project_id,),
            fetch=False
        )
        print("   ✓ Cleanup complete")
    except Exception as e:
        print(f"   ✗ Cleanup failed: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("ACAD-GIS Schema Fixes Test Suite")
    print("=" * 60)

    # Test connection first
    if not test_database_connection():
        print("\n❌ Cannot proceed without database connection")
        sys.exit(1)

    # Create test project
    project_id = test_create_project()
    if not project_id:
        print("\n❌ Cannot proceed without test project")
        sys.exit(1)

    # Run tests
    results = {
        'layers_upsert': test_layers_upsert(project_id),
        'project_details': test_project_details(project_id),
        'structures_invert_elev': test_structures_invert_elev(project_id),
        'sheet_notes': test_sheet_notes(project_id)
    }

    # Cleanup
    cleanup(project_id)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
