# Git Workflow for ACAD-GIS

**Created:** October 19, 2025  
**Purpose:** Daily Git operations and best practices for solo development

---

## Git Basics

### What is Git?

**Version control system** that tracks changes to files:
- **Time machine:** Go back to any previous version
- **Backup:** Code stored on GitHub (cloud)
- **Experimentation:** Try changes without fear of breaking things
- **Documentation:** Commit messages explain what changed and why

### Key Concepts

**Repository (repo):** The project folder with Git tracking (`.git/` directory)

**Commit:** A saved snapshot of your project at a point in time

**Branch:** A parallel version of your code (we use `main`)

**Remote:** The GitHub copy of your repo (called `origin`)

**Working directory:** Your current files (what you see in VS Code)

**Staging area:** Files prepared for next commit

---

## Daily Workflow

### Morning: Start Work
```bash
# 1. Navigate to project
cd ~/projects/acad-gis

# 2. Activate virtual environment
source venv/bin/activate

# 3. Check current status
git status

# 4. Pull latest changes from GitHub
git pull origin main

# 5. Check which branch you're on
git branch
# Should show: * main
```

### During Development

**Check what changed:**
```bash
git status
```

**Output example:**
```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  modified:   backend/api_server.py
  modified:   docs/PROJECT_CONTEXT.md

Untracked files:
  frontend/tools/project_manager.html
```

**View specific changes:**
```bash
# See line-by-line differences
git diff

# See diff for specific file
git diff backend/api_server.py
```

### Saving Work (Committing)

**Three-step process:**

**1. Stage changes:**
```bash
# Stage all changed files
git add .

# OR stage specific files
git add backend/api_server.py
git add frontend/tools/project_manager.html
```

**2. Commit with message:**
```bash
git commit -m "feat: Extract project manager tool from dashboard"
```

**3. Push to GitHub:**
```bash
git push origin main
# or just:
git push
```

### End of Day
```bash
# 1. Check for uncommitted changes
git status

# 2. If changes exist, commit them
git add .
git commit -m "wip: End of day save - working on map viewer"
git push

# 3. Verify on GitHub
# Visit: https://github.com/Rtoony/acad-gis
```

---

## Commit Message Best Practices

### Format
```
<type>: <description>

[optional body]
```

### Types
```
feat:     New feature
fix:      Bug fix
docs:     Documentation changes
refactor: Code restructuring (no functionality change)
style:    Formatting, whitespace (no code change)
test:     Adding tests
chore:    Maintenance (dependencies, config)
wip:      Work in progress (end of day saves)
```

### Examples

**Good commit messages:**
```bash
git commit -m "feat: Add project manager tool with CRUD operations"
git commit -m "fix: Resolve CORS issue in API server"
git commit -m "docs: Add database connection troubleshooting guide"
git commit -m "refactor: Extract CSS to shared styles file"
git commit -m "chore: Update dependencies to latest versions"
```

**Bad commit messages:**
```bash
git commit -m "changes"           # What changes?
git commit -m "fix"               # Fix what?
git commit -m "asdf"              # Meaningless
git commit -m "updated files"     # Which files? Why?
```

---

## Common Operations

### View History
```bash
# Compact view
git log --oneline

# Output:
# 4ef8d94 Fix: Install FastAPI dependencies instead of Flask
# bc42c74 Add core backend files and dashboard archive
# 196a688 Add Python dependencies
# acfddac Initial project structure and folders
```
```bash
# Detailed view
git log

# Shows full commit details:
# - Commit hash
# - Author
# - Date
# - Full message
```

### View Changes
```bash
# See what changed in last commit
git show

# See what changed in specific commit
git show 4ef8d94

# Compare two commits
git diff 196a688 4ef8d94
```

### Undo Changes

**Scenario 1: Undo changes to file (not yet staged)**
```bash
# Restore file to last committed version
git restore backend/api_server.py

# Restore all changed files
git restore .
```

**Scenario 2: Unstage file (staged but not committed)**
```bash
# Remove from staging area, keep changes
git restore --staged backend/api_server.py
```

**Scenario 3: Undo last commit (keep changes)**
```bash
# Undo commit, keep files changed
git reset --soft HEAD~1

# Now you can modify and re-commit
```

**Scenario 4: Undo last commit (discard changes)**
```bash
# CAREFUL: This deletes your changes!
git reset --hard HEAD~1
```

### Ignore the .env Warning

If you see:
```
warning: in the working copy of 'backend/.env', LF will be replaced by CRLF
```

This is normal and safe to ignore. It's just a line-ending difference between Windows and Linux.

---

## Branching (For Experiments)

### Why Branch?

**Problem:** Want to try major change but scared to break working code

**Solution:** Create a branch (parallel universe)

### Basic Branching
```bash
# Create and switch to new branch
git checkout -b feature/map-viewer-redesign

# Make changes, commit normally
git add .
git commit -m "feat: Redesign map viewer layout"

# If it works, merge back to main
git checkout main
git merge feature/map-viewer-redesign

# If it doesn't work, just go back to main
git checkout main
# Your main branch is untouched!
```

### Branch Strategy

**For ACAD-GIS (solo dev):**

**Option 1: Direct to main (current approach)**
- Work directly on `main` branch
- Commit often
- Push frequently

**Pros:** Simple, fast, no overhead  
**Cons:** Can't easily experiment

**Option 2: Feature branches (when experimenting)**
- Keep `main` stable
- Create branch for risky changes
- Merge when confirmed working

**Recommendation:** Start with Option 1, use Option 2 when needed

---

## GitHub Integration

### Repository URL
```
Web:  https://github.com/Rtoony/acad-gis
SSH:  git@github.com:Rtoony/acad-gis.git
```

### View on GitHub
```bash
# From project directory
git remote -v
# Shows: origin  git@github.com:Rtoony/acad-gis.git
```

**Visit in browser:**
https://github.com/Rtoony/acad-gis

### What's Stored on GitHub

**Included (tracked):**
- All code files
- Documentation (.md files)
- Configuration files (except .env)
- Project structure

**Excluded (in .gitignore):**
- `venv/` directory
- `.env` file (secrets!)
- `__pycache__/` directories
- `.pyc` compiled files

---

## Viewing Changes on GitHub

### Commits Page

https://github.com/Rtoony/acad-gis/commits/main

Shows:
- Commit history
- Who made changes
- When changes were made
- What changed in each commit

### Comparing Versions

**Compare two commits:**
```
https://github.com/Rtoony/acad-gis/compare/196a688...4ef8d94
```

**See files changed:**
- Green lines: Added
- Red lines: Removed
- Side-by-side comparison

---

## Collaboration (Future)

### If Adding Another Developer

**1. Add as collaborator:**
- GitHub repo → Settings → Collaborators
- Enter their GitHub username

**2. They clone repo:**
```bash
git clone git@github.com:Rtoony/acad-gis.git
cd acad-gis
```

**3. Their workflow:**
```bash
# Always pull before starting work
git pull

# Make changes, commit, push
git add .
git commit -m "feat: Add new feature"
git push
```

### Merge Conflicts (When Both Edit Same File)

**Git will flag conflicts:**
```
CONFLICT (content): Merge conflict in backend/api_server.py
```

**Resolve manually:**
```python
# File will look like:
<<<<<<< HEAD
your version
=======
their version
>>>>>>> branch-name

# Edit to keep what you want
# Remove conflict markers
# Save file
```

**Then commit:**
```bash
git add backend/api_server.py
git commit -m "fix: Resolve merge conflict"
git push
```

---

## Troubleshooting

### "Your branch is behind 'origin/main'"

**Meaning:** GitHub has newer commits than your local copy

**Solution:**
```bash
git pull
```

### "Your branch is ahead of 'origin/main'"

**Meaning:** You have local commits not pushed to GitHub

**Solution:**
```bash
git push
```

### "fatal: not a git repository"

**Meaning:** You're not in the project directory

**Solution:**
```bash
cd ~/projects/acad-gis
```

### "Permission denied (publickey)"

**Meaning:** SSH key not configured or not added to GitHub

**Solution:**
```bash
# Test SSH connection
ssh -T git@github.com

# If fails, check SSH key
cat ~/.ssh/id_ed25519.pub
# Re-add to GitHub if needed
```

### "Changes not staged for commit"

**Meaning:** You have unsaved changes

**Solution:**
```bash
# See what changed
git status

# Stage and commit
git add .
git commit -m "Your message"
```

### Accidentally committed .env file

**Fix immediately:**
```bash
# Remove from Git but keep file
git rm --cached backend/.env

# Commit the removal
git commit -m "fix: Remove .env from Git tracking"

# Push to GitHub
git push

# Verify .gitignore has .env
cat .gitignore | grep .env
```

---

## Advanced Operations

### Stashing (Save Work Without Committing)
```bash
# Temporarily save changes
git stash

# Do other work (switch branches, pull, etc.)

# Restore saved changes
git stash pop
```

### Viewing File History
```bash
# See all commits that changed a file
git log -- backend/api_server.py

# See what changed in each commit
git log -p -- backend/api_server.py
```

### Blaming (Who Changed This Line?)
```bash
git blame backend/api_server.py

# Shows who wrote each line and when
```

---

## Git Aliases (Shortcuts)

Add to `~/.gitconfig`:
```bash
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = restore --staged
    last = log -1 HEAD
    visual = log --oneline --graph --all
```

**Usage:**
```bash
git st        # Instead of: git status
git co main   # Instead of: git checkout main
git br        # Instead of: git branch
git last      # Show last commit
git visual    # Pretty graph of commits
```

---

## Best Practices for ACAD-GIS

### Commit Frequency

**✅ Good:**
- Commit after completing a feature
- Commit when reaching a working state
- Commit at end of day (even if incomplete)

**❌ Bad:**
- Committing every line change (too granular)
- Only committing once a week (too infrequent)
- Committing broken code (unless marked `wip:`)

### When to Push

**Always push when:**
- End of work session
- After completing a feature
- Before switching machines
- Daily at minimum

**Don't need to push:**
- After every single commit
- When code is broken (unless marked `wip:`)

---

## Quick Reference

### Most Common Commands
```bash
# Check status
git status

# Stage all changes
git add .

# Commit
git commit -m "message"

# Push to GitHub
git push

# Pull from GitHub
git pull

# View history
git log --oneline

# See changes
git diff

# Undo changes to file
git restore filename
```

### Emergency Commands
```bash
# Forgot to commit? Undo last commit, keep changes
git reset --soft HEAD~1

# Committed wrong files? Unstage everything
git restore --staged .

# Everything broken? Go back to last commit
git reset --hard HEAD

# Really broken? Go back to working GitHub version
git fetch origin
git reset --hard origin/main
```

---

## Next Steps

- Practice committing small changes frequently
- Read commit history to understand what changed
- Experiment with branches for risky changes
- Set up aliases for faster workflow

---

**Remember:** Git is your safety net. Commit often, push daily, and you'll never lose work!

**Related docs:**
- DEVELOPMENT_ENVIRONMENT.md (environment setup)
- PROJECT_CONTEXT.md (project overview for LLMs)
