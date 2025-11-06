# Replit to Claude Code Integration Workflow

## Overview
This guide describes how to integrate Replit prototypes with the main acad-gis GitHub repository using Claude Code as the integration and refinement layer.

## Architecture

```
Replit (Rapid Prototyping) → GitHub (Version Control) → Claude Code (Integration & Polish)
```

## Setup: Connect Replit to GitHub

### For Each Replit Project:

1. **Initialize Git in Replit:**
   ```bash
   # In Replit Shell
   git config --global user.email "your-email@example.com"
   git config --global user.name "Your Name"
   ```

2. **Connect to GitHub:**
   ```bash
   # Option A: Clone if starting fresh
   git clone https://github.com/Rtoony/acad-gis.git
   cd acad-gis

   # Option B: Add remote to existing Replit project
   git init
   git remote add origin https://github.com/Rtoony/acad-gis.git
   git fetch origin
   ```

3. **Create Feature Branch:**
   ```bash
   git checkout -b replit-prototype-[feature-name]
   # Example: replit-prototype-survey-tool
   ```

## Workflow: Prototype → Integration

### Phase 1: Build in Replit

1. **Rapid development** in Replit with live Supabase connection
2. **Commit frequently** to your feature branch:
   ```bash
   git add .
   git commit -m "Prototype: [feature] - [what you built]"
   git push -u origin replit-prototype-[feature-name]
   ```

### Phase 2: Integration in Claude Code

Once your Replit prototype is working, switch to Claude Code:

1. **Fetch the prototype branch:**
   ```bash
   git fetch origin replit-prototype-[feature-name]
   git checkout replit-prototype-[feature-name]
   ```

2. **Use Claude Code to:**
   - Review code quality and patterns
   - Refactor to match acad-gis architecture
   - Add proper error handling
   - Write tests (using the testing framework in `QUICK_START_TESTING.md`)
   - Update documentation
   - Ensure database schema compatibility

3. **Decision Point - Where to place the code:**

   **Option A: Keep as Prototype** (recommended initially)
   ```bash
   # Move to prototypes folder
   mkdir -p prototypes/[feature-name]
   mv [replit-files] prototypes/[feature-name]/
   ```

   **Option B: Integrate into Main** (when production-ready)
   ```bash
   # Integrate into backend/ or frontend/tools/
   # Follow existing patterns in api_server.py, database.py, etc.
   ```

4. **Commit polished version:**
   ```bash
   git add .
   git commit -m "Integration: Polish and test [feature] from Replit prototype"
   git push origin replit-prototype-[feature-name]
   ```

5. **Create Pull Request** (optional, for review):
   ```bash
   # Use GitHub UI or if you have gh CLI
   gh pr create --title "Add [feature] from Replit prototype" \
     --body "Integrated and polished prototype built in Replit"
   ```

6. **Merge to main branch:**
   ```bash
   git checkout main
   git merge replit-prototype-[feature-name]
   git push origin main
   ```

## Database Coordination

Since both Replit and acad-gis use the same Supabase database:

### Best Practices:

1. **Use separate test projects** in the database:
   ```sql
   -- In Replit prototype
   INSERT INTO projects (name, description)
   VALUES ('REPLIT_TEST_[feature]', 'Testing prototype feature');
   ```

2. **Document schema changes:**
   - If your Replit prototype needs new tables/columns, document in migration file
   - Use `backend/run_migrations.py` pattern when integrating

3. **Avoid conflicts:**
   - Don't modify existing production data in prototypes
   - Use project/drawing prefixes like `REPL_`, `PROTO_`, `TEST_`

## Claude Code Strengths for Integration

Use your Claude Code credits effectively for:

1. **Code Quality Review:**
   - "Review this Replit prototype code and suggest improvements"
   - "Refactor this to match the patterns in backend/api_server.py"

2. **Testing:**
   - "Write tests for this prototype feature using the test framework"
   - "Add error handling and validation"

3. **Documentation:**
   - "Document this API endpoint in docs/API.md"
   - "Create user guide for this tool"

4. **Integration Tasks:**
   - "Integrate this Replit Flask app into the FastAPI backend"
   - "Convert this standalone tool to match the frontend/tools/ pattern"

5. **Database Migration:**
   - "Create a migration script for these schema changes"
   - "Update database.py with these new queries"

## Example: Integrating a Survey Tool

### Step 1: In Replit
```bash
# Build survey-tool prototype, test with Supabase
git add .
git commit -m "Prototype: Survey point collection tool"
git push origin replit-prototype-survey-tool
```

### Step 2: In Claude Code
```bash
# Switch to prototype branch
git fetch origin replit-prototype-survey-tool
git checkout replit-prototype-survey-tool

# Ask Claude Code:
# "Review this Replit survey tool prototype and integrate it into
#  backend/survey_api.py following the existing patterns. Add tests
#  and update the API documentation."

# After Claude Code integrates:
git add .
git commit -m "Integration: Survey tool from Replit, added tests and docs"
git push origin replit-prototype-survey-tool

# Merge to main
git checkout main
git merge replit-prototype-survey-tool
git push origin main
```

## File Organization

```
acad-gis/
├── prototypes/
│   ├── replit-[feature-1]/     # Raw Replit prototypes
│   ├── replit-[feature-2]/     # Kept for reference
│   └── joshycad/               # Existing prototypes
├── backend/
│   ├── api_server.py           # Production-ready integrations
│   ├── survey_api.py           # Integrated from Replit
│   └── [feature]_api.py        # Other integrations
├── frontend/tools/
│   └── [feature]-tool.html     # Frontend for Replit features
└── docs/
    └── [FEATURE]_GUIDE.md      # Documentation for each tool

```

## Tips for Success

1. **Commit often in Replit** - don't lose work
2. **Use descriptive branch names** - `replit-prototype-survey`, `replit-prototype-bmp-editor`
3. **Keep prototypes functional** - don't delete from prototypes/ folder immediately
4. **Document database changes** - schema migrations are critical
5. **Test in Claude Code environment** - ensure it works outside Replit
6. **Leverage Claude Code credits** for refactoring and integration work

## Quick Commands Reference

```bash
# In Replit: Push prototype
git add . && git commit -m "Prototype: [description]" && git push

# In Claude Code: Fetch and integrate
git fetch origin [branch-name]
git checkout [branch-name]
# Work with Claude Code to integrate
git add . && git commit -m "Integration: [description]" && git push

# Merge to main
git checkout main
git merge [branch-name]
git push origin main
```

## Troubleshooting

**Issue: Replit and GitHub out of sync**
```bash
git fetch origin
git status
git pull origin [branch-name] --rebase
```

**Issue: Different dependencies**
- Document in requirements.txt
- Test in Claude Code environment before merging

**Issue: Database schema mismatch**
- Create migration script in backend/
- Update SCHEMA_MIGRATION_GUIDE.md

## Next Steps

1. Choose your first Replit prototype to integrate
2. Set up Git connection in Replit
3. Push to a feature branch
4. Use Claude Code to polish and integrate
5. Repeat for other prototypes

---

**Remember:** Replit is for rapid experimentation, Claude Code is for production-quality integration. Use both tools for their strengths!
