"""
Testing Project API Endpoints
Tests: Create, List, Update, Delete projects
"""

import requests
import uuid

# Your API base URL
API_BASE = "http://localhost:8000/api"


def test_create_project():
    """
    Test creating a new project
    """
    # Create a unique project name so we don't get duplicates
    project_name = f"Test Project {uuid.uuid4().hex[:8]}"

    # Data to send to the API
    project_data = {
        "project_name": project_name,
        "client": "Test Client",
        "description": "This is a test project created by automated tests"
    }

    # Make POST request to create project
    response = requests.post(f"{API_BASE}/projects", json=project_data)

    # Check it worked
    assert response.status_code == 200

    # Check we got back a project with an ID
    result = response.json()
    assert "project_id" in result or "project" in result

    print(f"✅ Created project: {project_name}")


def test_list_projects():
    """
    Test getting list of projects
    """
    # Make GET request to list projects
    response = requests.get(f"{API_BASE}/projects")

    # Check it worked
    assert response.status_code == 200

    # Check we got back data
    data = response.json()
    assert data is not None

    print(f"✅ Got projects list successfully")


def test_api_health():
    """
    Test the health check endpoint
    """
    response = requests.get(f"{API_BASE}/health")

    assert response.status_code == 200

    data = response.json()
    # The response should have some status indicator
    assert data is not None
    assert isinstance(data, dict)

    print("✅ API health check passed")


def test_api_stats():
    """
    Test the stats endpoint
    """
    response = requests.get(f"{API_BASE}/stats")

    assert response.status_code == 200

    data = response.json()
    # Should return some statistics
    assert data is not None
    assert isinstance(data, dict)

    print("✅ API stats endpoint works")


def test_list_drawings():
    """
    Test getting list of drawings
    """
    response = requests.get(f"{API_BASE}/drawings")

    assert response.status_code == 200

    data = response.json()
    assert data is not None

    print("✅ Drawings list endpoint works")


def test_recent_activity():
    """
    Test the recent activity endpoint
    """
    response = requests.get(f"{API_BASE}/recent-activity")

    # Should work even if there's no activity
    assert response.status_code == 200

    data = response.json()
    assert data is not None

    print("✅ Recent activity endpoint works")
