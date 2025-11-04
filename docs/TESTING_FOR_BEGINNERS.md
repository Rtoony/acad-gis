# Testing Guide for Beginners

**Welcome!** This guide will teach you how to test your ACAD-GIS tool, even if you've never written a test before.

## What is Testing?

Testing means **checking that your code works correctly**. Instead of manually clicking through your app every time you make a change, you write code that automatically checks things for you.

Think of it like this:
- **Manual testing:** You click buttons, check if things work, repeat every time
- **Automated testing:** You write a test once, it runs in seconds, catches bugs automatically

---

## 🎯 Step 1: Run Your Existing Tests (2 minutes)

Good news! You already have tests. Let's run them to see what "testing" looks like.

### Test 1: Check Database Connection

```bash
cd /home/user/acad-gis
python backend/quick_test.py
```

**What this does:**
- Checks if your database is reachable
- Shows you how many projects/drawings you have
- Takes about 5 seconds

**What success looks like:**
```
✅ CONNECTION SUCCESSFUL!
✅ Found 3 projects in database
✅ Found 5 drawings in database
```

### Test 2: Smoke Test (checks basic API)

```bash
# First, make sure your API is running
python backend/api_server.py &

# Then run the smoke test
python scripts/smoke_test_survey_civil.py
```

**What this does:**
- Tests if your API endpoints work
- Creates test data (project, survey points, etc.)
- Verifies everything connects properly

**What success looks like:**
```
= RESULT: PASS
```

### Test 3: Unit Tests (tests specific functions)

```bash
pytest backend/test_pipe_validation.py -v
```

**What this does:**
- Tests pipe network validation logic
- Checks if slope calculations are correct
- Verifies design standards are applied

**What success looks like:**
```
test_get_min_slope_for_diameter PASSED
test_calculate_velocity PASSED
test_slope_validation_logic PASSED
=================== 12 passed in 0.43s ===================
```

---

## 🎯 Step 2: Understanding Test Output

When you run tests, you'll see one of three results:

### ✅ PASSED (Green)
The test worked! Your code is doing what it should.

### ❌ FAILED (Red)
The test found a problem. This is **good** - it caught a bug before users found it!

### ⚠️ ERROR (Yellow)
The test itself has a problem (not your code). Usually means missing dependencies or wrong setup.

**Example output:**
```
tests/test_example.py::test_create_project PASSED    [ 25%]
tests/test_example.py::test_list_projects PASSED     [ 50%]
tests/test_example.py::test_delete_project FAILED    [ 75%]  ← Bug found!
tests/test_example.py::test_api_health PASSED        [100%]

3 passed, 1 failed
```

---

## 🎯 Step 3: Your First Test (10 minutes)

Let's write a super simple test together. We'll test that your API is running.

### Create a test file:

```bash
mkdir -p tests
touch tests/test_my_first_test.py
```

### Write this code:

```python
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
```

### Run your test:

```bash
# Make sure API is running first
python backend/api_server.py &

# Run the test
pytest tests/test_my_first_test.py -v -s
```

**Flags explained:**
- `-v` = verbose (shows more details)
- `-s` = show print statements (so you see the ✅ messages)

**What you should see:**
```
tests/test_my_first_test.py::test_api_is_running PASSED
tests/test_my_first_test.py::test_math_works PASSED

=================== 2 passed in 0.12s ===================
```

---

## 🎯 Step 4: Testing Your API Endpoints (20 minutes)

Now let's test something real - your project API.

### Create a new test file:

```bash
touch tests/test_projects_api.py
```

### Write this code:

```python
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
        "description": "This is a test project"
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

    # Check we got back a list
    projects = response.json()
    assert isinstance(projects, (list, dict))  # Could be list or paginated dict

    print(f"✅ Got projects list")


def test_api_health():
    """
    Test the health check endpoint
    """
    response = requests.get(f"{API_BASE}/health")

    assert response.status_code == 200

    data = response.json()
    assert "database_status" in data or "status" in data

    print("✅ API health check passed")


def test_api_stats():
    """
    Test the stats endpoint
    """
    response = requests.get(f"{API_BASE}/stats")

    assert response.status_code == 200

    data = response.json()
    assert "total_projects" in data or "projects" in data

    print("✅ API stats endpoint works")
```

### Run these tests:

```bash
pytest tests/test_projects_api.py -v -s
```

**What you should see:**
```
tests/test_projects_api.py::test_create_project PASSED
tests/test_projects_api.py::test_list_projects PASSED
tests/test_projects_api.py::test_api_health PASSED
tests/test_projects_api.py::test_api_stats PASSED

=================== 4 passed in 0.45s ===================
```

---

## 🎯 Step 5: Testing Database Operations (15 minutes)

Let's test that your database works correctly.

### Create a test file:

```bash
touch tests/test_database.py
```

### Write this code:

```python
"""
Testing Database Operations
Tests: Connection, queries, data integrity
"""

import psycopg2
from dotenv import load_dotenv
import os

# Load database credentials
load_dotenv("backend/.env")

def get_db_connection():
    """
    Helper function to connect to database
    """
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )


def test_database_connection():
    """
    Test we can connect to the database
    """
    conn = get_db_connection()
    assert conn is not None

    cur = conn.cursor()
    cur.execute("SELECT 1")
    result = cur.fetchone()

    assert result[0] == 1

    cur.close()
    conn.close()

    print("✅ Database connection works")


def test_projects_table_exists():
    """
    Test that the projects table exists
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if projects table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'projects'
        )
    """)

    exists = cur.fetchone()[0]
    assert exists == True

    cur.close()
    conn.close()

    print("✅ Projects table exists")


def test_can_query_projects():
    """
    Test we can query projects from database
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM projects")
    count = cur.fetchone()[0]

    # Count should be a number (even if 0)
    assert isinstance(count, int)
    assert count >= 0

    cur.close()
    conn.close()

    print(f"✅ Database has {count} projects")


def test_postgis_installed():
    """
    Test that PostGIS extension is installed
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT EXISTS (
            SELECT FROM pg_extension
            WHERE extname = 'postgis'
        )
    """)

    has_postgis = cur.fetchone()[0]
    assert has_postgis == True

    cur.close()
    conn.close()

    print("✅ PostGIS is installed")
```

### Run these tests:

```bash
pytest tests/test_database.py -v -s
```

---

## 🎯 Step 6: Manual Testing with curl (Simple API Testing)

Sometimes you don't need fancy tests - you just want to check if an API works. Use `curl` for quick tests.

### Test 1: Health Check

```bash
curl http://localhost:8000/api/health
```

**Expected output:** JSON with database status

### Test 2: List Projects

```bash
curl http://localhost:8000/api/projects
```

**Expected output:** Array of projects

### Test 3: Create a Project

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"project_name":"curl Test Project","client":"Test Client"}'
```

**Expected output:** The created project with an ID

### Test 4: Get Project Stats

```bash
curl http://localhost:8000/api/stats
```

**Expected output:** JSON with counts of projects, drawings, etc.

---

## 🎯 Step 7: Running All Your Tests

Create a simple script to run all tests at once.

### Create the script:

```bash
touch run_tests.sh
chmod +x run_tests.sh
```

### Add this content:

```bash
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
    exit 1
fi

echo ""
echo "1. Running connection test..."
python backend/quick_test.py
echo ""

echo "2. Running unit tests..."
pytest backend/test_pipe_validation.py -v
echo ""

echo "3. Running API tests..."
pytest tests/ -v
echo ""

echo "4. Running smoke test..."
python scripts/smoke_test_survey_civil.py
echo ""

echo "======================================"
echo "All tests complete!"
echo "======================================"
```

### Run all tests:

```bash
./run_tests.sh
```

---

## 🎯 Step 8: Testing Your Frontend (Manual)

Frontend testing is simpler - you just click through and check things work.

### Create a testing checklist:

```bash
touch docs/FRONTEND_TEST_CHECKLIST.md
```

### Checklist content:

```markdown
# Frontend Testing Checklist

## Tool Launcher
- [ ] Open tool_launcher.html in browser
- [ ] No errors in console (F12 → Console)
- [ ] All tool cards visible
- [ ] Stats display correctly
- [ ] Each tool card opens correct page

## Project Manager
- [ ] Opens without errors
- [ ] Can see list of projects
- [ ] Can create new project
- [ ] Can edit project
- [ ] Can delete project
- [ ] Search works
- [ ] Pagination works (if >20 projects)

## Map Viewer
- [ ] Opens without errors
- [ ] Project dropdown populates
- [ ] Can select a project
- [ ] Map loads (see tiles)
- [ ] Features display on map
- [ ] Can click features (popup shows)
- [ ] Layer toggles work
- [ ] Zoom to extent button works

## Drawing Importer
- [ ] Opens without errors
- [ ] Can select project
- [ ] Can select file
- [ ] Upload button works
- [ ] Shows progress or success message
```

**How to use this:**
1. Open the file
2. Go through each item
3. Check the box if it works
4. Note any issues you find

---

## 🎯 Common Testing Scenarios

### Scenario 1: Test After Making Changes

**You just changed some code. Does it still work?**

```bash
# Quick check - just run the test for what you changed
pytest tests/test_projects_api.py -v

# Full check - run everything
./run_tests.sh
```

### Scenario 2: Test a New Feature

**You added a new API endpoint. How to test it?**

```bash
# Quick manual test with curl
curl http://localhost:8000/api/your-new-endpoint

# Write a proper test
# Add to tests/test_your_feature.py
def test_new_feature():
    response = requests.get("http://localhost:8000/api/your-new-endpoint")
    assert response.status_code == 200
```

### Scenario 3: Test Before Deploying

**You want to make sure everything works before pushing to production:**

```bash
# Run ALL tests
./run_tests.sh

# Only deploy if everything passes!
```

---

## 🎯 Understanding Test Results

### When a Test Fails

**Example failure:**
```
tests/test_projects_api.py::test_create_project FAILED

================================ FAILURES =================================
def test_create_project():
    response = requests.post(f"{API_BASE}/projects", json=project_data)
>   assert response.status_code == 200
E   assert 500 == 200

FAILED tests/test_projects_api.py::test_create_project - assert 500 == 200
```

**What this means:**
- Expected status code: 200 (success)
- Got status code: 500 (server error)
- **Your API has a bug!**

**How to debug:**
1. Check your API server logs
2. Look at the error message
3. Fix the bug
4. Run test again

---

## 🎯 Quick Reference

### Run all tests:
```bash
pytest tests/ -v
```

### Run one test file:
```bash
pytest tests/test_projects_api.py -v
```

### Run one specific test:
```bash
pytest tests/test_projects_api.py::test_create_project -v
```

### Show print statements:
```bash
pytest tests/test_projects_api.py -v -s
```

### Stop on first failure:
```bash
pytest tests/ -x
```

### See detailed error messages:
```bash
pytest tests/ -v --tb=long
```

---

## 🎯 Next Steps

1. **Run your existing tests** - Get comfortable with the process
2. **Write simple tests** - Start with the examples above
3. **Test as you code** - After adding a feature, write a test for it
4. **Build the habit** - Run tests before committing code

---

## ❓ FAQ

**Q: How do I know what to test?**
A: Test the main things your tool does:
- Can users create projects?
- Can users import DXF files?
- Does the map show data correctly?

**Q: How many tests should I write?**
A: Start with one test per major feature. You can always add more later.

**Q: What if I break a test?**
A: Good! That means the test caught a bug. Fix your code and run the test again.

**Q: Do I need to test everything?**
A: No. Focus on the critical paths - the things users do most often.

**Q: How long should tests take?**
A: Fast tests (< 1 second) are best. Your full test suite should run in under 1 minute.

---

## 🎉 You're Ready!

Testing isn't scary - it's just code that checks other code. Start simple, build confidence, and add more tests as you go.

**Remember:**
- Tests catch bugs before users do
- Tests give you confidence to make changes
- Tests document how your code should work
- Tests save you time in the long run

Now go run those tests! 🚀
