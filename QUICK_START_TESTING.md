# Quick Start: Testing in 5 Minutes

**New to testing?** Follow these steps to run your first tests right now!

---

## Step 1: Make Sure Your API is Running (1 minute)

Open a terminal and run:

```bash
cd /home/user/acad-gis
python backend/api_server.py
```

**What you should see:**
```
Server running at: http://localhost:8000
```

**Keep this terminal open!** Your API needs to be running for tests to work.

---

## Step 2: Run Your First Test (30 seconds)

Open a **NEW terminal** (keep the API running in the first one) and run:

```bash
cd /home/user/acad-gis
pytest tests/test_my_first_test.py -v -s
```

**What you should see:**
```
tests/test_my_first_test.py::test_api_is_running PASSED
tests/test_my_first_test.py::test_math_works PASSED
tests/test_my_first_test.py::test_strings_work PASSED

=================== 3 passed in 0.15s ===================
```

**🎉 Congratulations! You just ran your first automated tests!**

---

## Step 3: Test Your Database (30 seconds)

```bash
pytest tests/test_database.py -v -s
```

**What you should see:**
```
tests/test_database.py::test_database_connection PASSED
tests/test_database.py::test_projects_table_exists PASSED
tests/test_database.py::test_can_query_projects PASSED
tests/test_database.py::test_postgis_installed PASSED

✅ Database connection works
✅ Projects table exists
✅ Database has 5 projects
✅ PostGIS is installed
```

---

## Step 4: Test Your API (1 minute)

```bash
pytest tests/test_projects_api.py -v -s
```

**What you should see:**
```
tests/test_projects_api.py::test_create_project PASSED
tests/test_projects_api.py::test_list_projects PASSED
tests/test_projects_api.py::test_api_health PASSED
tests/test_projects_api.py::test_api_stats PASSED

✅ Created project: Test Project abc123
✅ Got projects list successfully
✅ API health check passed
✅ API stats endpoint works
```

---

## Step 5: Run ALL Tests at Once (2 minutes)

```bash
./run_tests.sh
```

This runs:
1. ✅ Connection test
2. ✅ Unit tests (pipe validation)
3. ✅ Database tests
4. ✅ API tests
5. ✅ Smoke test

**What success looks like:**
```
✅ All tests complete!
```

---

## Quick Manual Test with curl

Want to test an API endpoint manually? Use `curl`:

### Test 1: Check if API is healthy
```bash
curl http://localhost:8000/api/health
```

### Test 2: List your projects
```bash
curl http://localhost:8000/api/projects
```

### Test 3: Create a project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"project_name":"My Test Project","client":"Test Client"}'
```

### Test 4: Get stats
```bash
curl http://localhost:8000/api/stats
```

---

## Understanding Test Results

### ✅ PASSED (Green) = Good!
Your code works as expected

### ❌ FAILED (Red) = Found a bug!
This is actually good - the test caught a problem before users did

### Example of a pass:
```
test_api_is_running PASSED    [100%]
=================== 1 passed in 0.05s ===================
```

### Example of a fail:
```
test_create_project FAILED    [100%]
E   assert 500 == 200
E   Expected: 200 (success)
E   Got: 500 (server error)

=================== 1 failed in 0.12s ===================
```

When you see a failure:
1. Read the error message
2. Check your API server logs
3. Fix the bug
4. Run the test again

---

## Common Commands

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

### Show print statements (helpful for debugging):
```bash
pytest tests/ -v -s
```

### Stop on first failure (saves time):
```bash
pytest tests/ -x
```

---

## What Each Test Does

### `test_my_first_test.py`
- Tests basic math (silly but shows how tests work)
- Tests if API is running
- Tests string operations

### `test_database.py`
- Tests database connection
- Checks if tables exist
- Verifies PostGIS is installed
- Counts projects and drawings

### `test_projects_api.py`
- Tests creating a project
- Tests listing projects
- Tests API health check
- Tests statistics endpoint

### `test_pipe_validation.py` (already existed)
- Tests pipe network validation
- Tests slope calculations
- Tests velocity calculations
- Tests design standards

---

## Troubleshooting

### Problem: "Connection refused"
**Solution:** Your API isn't running. Start it:
```bash
python backend/api_server.py
```

### Problem: "ModuleNotFoundError: No module named 'pytest'"
**Solution:** Install pytest:
```bash
pip install pytest
```

### Problem: "psycopg2.OperationalError: could not connect"
**Solution:** Check your database connection:
```bash
python backend/quick_test.py
```

### Problem: Tests are slow
**Solution:** That's normal for API tests. They need to actually call the API. If it takes >10 seconds, something might be wrong.

---

## Next Steps

1. ✅ **Run the tests above** - Get comfortable with the process
2. ✅ **Read the full guide** - Open `docs/TESTING_FOR_BEGINNERS.md`
3. ✅ **Test your frontend** - Use `docs/FRONTEND_TEST_CHECKLIST.md`
4. ✅ **Write your own test** - Copy one of the examples and modify it
5. ✅ **Make it a habit** - Run tests before committing code

---

## Help & Resources

- **Full testing guide:** `docs/TESTING_FOR_BEGINNERS.md`
- **Frontend checklist:** `docs/FRONTEND_TEST_CHECKLIST.md`
- **API test samples:** `docs/API_TEST_SAMPLES.md`
- **Existing tests:** Look in `backend/test_*.py` and `tests/test_*.py`

---

## Summary

**Testing is simple:**
1. Write code that checks your code
2. Run `pytest` to check everything works
3. Fix any failures
4. Commit with confidence!

**You now know how to:**
- ✅ Run existing tests
- ✅ Run all tests at once
- ✅ Test your API with curl
- ✅ Understand test results
- ✅ Debug test failures

**Now go test! 🚀**
