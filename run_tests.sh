#!/bin/bash

echo "======================================"
echo "ACAD-GIS Testing Suite"
echo "======================================"
echo ""

# Check if API is running
echo "Checking if API is running..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ API is running"
else
    echo "❌ API is not running. Start it with: python backend/api_server.py"
    echo ""
    echo "To start the API:"
    echo "  cd /home/user/acad-gis"
    echo "  python backend/api_server.py"
    exit 1
fi

echo ""
echo "======================================"
echo "1. Running Connection Test"
echo "======================================"
python backend/quick_test.py
echo ""

echo "======================================"
echo "2. Running Unit Tests (Pipe Validation)"
echo "======================================"
pytest backend/test_pipe_validation.py -v
echo ""

echo "======================================"
echo "3. Running Database Tests"
echo "======================================"
pytest tests/test_database.py -v -s
echo ""

echo "======================================"
echo "4. Running API Tests"
echo "======================================"
pytest tests/test_my_first_test.py -v -s
pytest tests/test_projects_api.py -v -s
echo ""

echo "======================================"
echo "5. Running Smoke Test"
echo "======================================"
python scripts/smoke_test_survey_civil.py
echo ""

echo "======================================"
echo "✅ All tests complete!"
echo "======================================"
