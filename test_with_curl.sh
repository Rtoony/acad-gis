#!/bin/bash

# Simple Manual API Testing with curl
# This script shows you how to test your API without writing code

echo "======================================"
echo "Manual API Testing with curl"
echo "======================================"
echo ""

# Check if API is running
echo "Checking if API is running..."
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "❌ API is not running!"
    echo ""
    echo "Start it with:"
    echo "  python backend/api_server.py"
    exit 1
fi
echo "✅ API is running"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "Command: curl http://localhost:8000/api/health"
echo "Result:"
curl -s http://localhost:8000/api/health | python -m json.tool
echo ""
echo ""

# Test 2: Get Statistics
echo "Test 2: Get Statistics"
echo "Command: curl http://localhost:8000/api/stats"
echo "Result:"
curl -s http://localhost:8000/api/stats | python -m json.tool
echo ""
echo ""

# Test 3: List Projects
echo "Test 3: List Projects"
echo "Command: curl http://localhost:8000/api/projects"
echo "Result:"
curl -s http://localhost:8000/api/projects | python -m json.tool | head -30
echo "(truncated for readability)"
echo ""
echo ""

# Test 4: Create a Project
echo "Test 4: Create a Project"
PROJECT_NAME="Test Project $(date +%s)"
echo "Command: curl -X POST ... (creating '$PROJECT_NAME')"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d "{\"project_name\":\"$PROJECT_NAME\",\"client\":\"Test Client\",\"description\":\"Created by test script\"}")
echo "Result:"
echo "$RESPONSE" | python -m json.tool
echo ""
echo ""

# Test 5: List Drawings
echo "Test 5: List Drawings"
echo "Command: curl http://localhost:8000/api/drawings"
echo "Result:"
curl -s http://localhost:8000/api/drawings | python -m json.tool | head -30
echo "(truncated for readability)"
echo ""
echo ""

# Test 6: Recent Activity
echo "Test 6: Recent Activity"
echo "Command: curl http://localhost:8000/api/recent-activity"
echo "Result:"
curl -s http://localhost:8000/api/recent-activity | python -m json.tool
echo ""
echo ""

echo "======================================"
echo "✅ All manual tests complete!"
echo "======================================"
echo ""
echo "To test other endpoints, use this pattern:"
echo "  curl http://localhost:8000/api/YOUR-ENDPOINT"
echo ""
echo "To see formatted JSON, pipe to python:"
echo "  curl http://localhost:8000/api/health | python -m json.tool"
echo ""
echo "Available endpoints to try:"
echo "  - /api/health"
echo "  - /api/stats"
echo "  - /api/projects"
echo "  - /api/drawings"
echo "  - /api/recent-activity"
echo "  - /api/pipe-networks"
echo "  - /api/alignments"
echo "  - /api/survey-points"
echo ""
