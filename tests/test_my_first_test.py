"""
My First Test - Testing the ACAD-GIS API
This is a simple test to check if the API is running
"""

import requests


def test_api_is_running():
    """
    This test checks if the API health endpoint responds
    """
    # 1. Make a request to the API
    response = requests.get("http://localhost:8000/api/health")

    # 2. Check if we got a successful response (status code 200)
    assert response.status_code == 200

    # 3. Check if the response contains JSON data
    data = response.json()
    assert data is not None

    print("✅ API is running and healthy!")


def test_math_works():
    """
    A silly test to show you how tests work
    """
    # These should pass
    assert 2 + 2 == 4
    assert 10 - 5 == 5
    assert 3 * 3 == 9

    print("✅ Math still works!")


def test_strings_work():
    """
    Another simple test to build confidence
    """
    name = "ACAD-GIS"

    assert name == "ACAD-GIS"
    assert len(name) == 8
    assert "GIS" in name

    print("✅ String operations work!")
