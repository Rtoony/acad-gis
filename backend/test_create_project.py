from database import create_project, get_project
import uuid

print("Creating test project...")
try:
    project_id = create_project(
        project_name="WSL Connection Test",
        project_number="TEST-001",
        description="Testing connection from WSL"
    )
    print(f"✅ Created project: {project_id}")
    
    # Verify we can read it back
    project = get_project(project_id)
    print(f"✅ Retrieved project: {project['project_name']}")
    print(f"✅ Project number: {project['project_number']}")
except Exception as e:
    print(f"❌ Error: {e}")
