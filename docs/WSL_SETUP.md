# WSL Development Environment Setup

**Created:** October 19, 2025  
**System:** Windows 11 + WSL (Ubuntu 24.04)  
**Purpose:** Professional Python development environment for ACAD-GIS project

---

## Overview

This document details the complete setup of Windows Subsystem for Linux (WSL) as a professional development environment. This setup enables:

- Native Linux Python development
- Git version control
- GitHub integration via SSH
- Professional terminal experience
- VS Code integration with remote WSL editing

---

## Why WSL?

### Problems with Windows-Native Python Development
1. **Path inconsistencies:** `C:\Users\Josh\Desktop\` vs Linux-style paths
2. **Package compatibility:** Many Python packages assume Linux
3. **Git integration:** Git was designed for Linux, works better there
4. **Documentation:** Most tutorials/Stack Overflow assume Linux
5. **Production parity:** Servers run Linux, so develop on Linux

### What WSL Provides
1. **Real Linux kernel:** Full Ubuntu running inside Windows
2. **File system access:** Can access Windows files from `/mnt/c/`
3. **Native tooling:** bash, apt, ssh work as expected
4. **VS Code integration:** Edit files in WSL from VS Code GUI
5. **No dual boot:** Linux + Windows simultaneously

---

## Installation Steps

### 1. Install WSL

**From PowerShell (Administrator):**
```powershell
wsl --install
```

**Verify installation:**
```bash
wsl --status
```

**Expected output:**
```
Default Distribution: Ubuntu
Default Version: 2
```

### 2. Install Windows Terminal

**Why:** Better than default terminal
- Multiple tabs
- Split panes  
- Profiles for PowerShell, WSL, CMD
- Better rendering

**Download:** Microsoft Store → "Windows Terminal"

**Default to WSL:**
1. Open Windows Terminal
2. Settings (Ctrl+,)
3. Startup → Default profile → Ubuntu

---

## Initial WSL Configuration

### Update System Packages
```bash
# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install essential development tools
sudo apt install -y python3-pip python3-venv git curl build-essential
```

**What each does:**
- `python3-pip`: Python package installer
- `python3-venv`: Virtual environment creation
- `git`: Version control
- `curl`: Download files from command line
- `build-essential`: C compiler (needed for some Python packages)

---

## Git Configuration

### Set Your Identity

Git labels every commit with your name and email. Configure these:
```bash
git config --global user.name "Josh Patheal"
git config --global user.email "joshpatheal@gmail.com"
git config --global init.defaultBranch main
```

**Verify:**
```bash
git config --global --list
```

**Expected output:**
```
user.name=Josh Patheal
user.email=joshpatheal@gmail.com
init.defaultbranch=main
```

### Important Notes
- **NOT creating GitHub account:** This just tells Git who you are locally
- **Email MUST match GitHub:** Use the same email you used for github.com
- **Name is display name:** Appears in commit history

---

## GitHub SSH Setup

### Why SSH Instead of HTTPS?

**HTTPS (old way):**
```bash
git clone https://github.com/Rtoony/acad-gis.git
# Requires username/password every time you push
```

**SSH (pro way):**
```bash
git clone git@github.com:Rtoony/acad-gis.git
# Automatic authentication via SSH key
```

### Generate SSH Key
```bash
ssh-keygen -t ed25519 -C "joshpatheal@gmail.com"
```

**Prompts and responses:**
```
Enter file in which to save the key: [Press ENTER - accept default]
Enter passphrase: [Press ENTER - no passphrase]
Enter same passphrase again: [Press ENTER]
```

**Result:** Two files created:
- `~/.ssh/id_ed25519` (private key - NEVER share)
- `~/.ssh/id_ed25519.pub` (public key - safe to share)

### Copy Public Key
```bash
cat ~/.ssh/id_ed25519.pub
```

**Output example:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP/tlRDkRp65BmSLh046cvO447rRPWYsBlxEF3Sx4eG1 joshpatheal@gmail.com
```

**Copy this ENTIRE line** (including `joshpatheal@gmail.com` at the end).

### Add Key to GitHub

1. Go to: https://github.com/settings/keys
2. Click **"New SSH key"**
3. **Title:** `WSL - Desktop PC`
4. **Key type:** Authentication Key
5. **Key:** Paste the line from above
6. Click **"Add SSH key"**
7. Enter your GitHub password if prompted

### Test Connection
```bash
ssh -T git@github.com
```

**Expected output:**
```
Hi Rtoony! You've successfully authenticated, but GitHub does not provide shell access.
```

**If you see "Hi Rtoony!"** → Success! ✅

---

## File System Navigation

### Windows → WSL

Your Windows drives are mounted in WSL:
```bash
# Windows: C:\Users\Josh\Desktop\
# WSL:     /mnt/c/Users/Josh/Desktop/

# Navigate to Windows Desktop from WSL
cd /mnt/c/Users/Josh/Desktop/
```

### WSL → Windows

Your WSL home directory is accessible from Windows:

**Path format:**
```
\\wsl$\Ubuntu\home\josh_patheal\
```

**Open in File Explorer:**
```bash
# From WSL, open current directory in Windows Explorer
explorer.exe .
```

---

## Project Directory Structure

### Standard Linux Location
```bash
# Create projects folder in WSL home
mkdir -p ~/projects

# Navigate there
cd ~/projects
```

**Why ~/projects and not Desktop?**
- Linux convention: Projects in `~/projects` or `~/src`
- Faster: WSL filesystem is faster than accessing `/mnt/c/`
- Cleaner: Separates Linux work from Windows desktop clutter

### Your Project Path
```
WSL Path:      /home/josh_patheal/projects/acad-gis/
Windows Path:  \\wsl$\Ubuntu\home\josh_patheal\projects\acad-gis\
```

---

## Terminal Workflow

### Basic Navigation
```bash
# Go home
cd ~

# Go to project
cd ~/projects/acad-gis

# Go up one directory
cd ..

# List files (detailed)
ls -la

# Show current directory path
pwd
```

### Useful Aliases

Add to `~/.bashrc` for shortcuts:
```bash
# Edit .bashrc
nano ~/.bashrc

# Add these lines at the end:
alias ll='ls -lah'
alias projects='cd ~/projects'
alias acad='cd ~/projects/acad-gis'
alias activate='source venv/bin/activate'

# Save: Ctrl+X, Y, Enter

# Reload
source ~/.bashrc
```

**Now you can type:**
- `acad` → Goes to project
- `ll` → Lists files in detail
- `activate` → Activates virtual environment

---

## Virtual Environment Best Practices

### What is a Virtual Environment?

**Problem:** System-wide Python packages can conflict
```bash
pip install package==1.0  # Project A needs version 1.0
pip install package==2.0  # Project B needs version 2.0 - BREAKS Project A!
```

**Solution:** Isolated environment per project
```bash
# Project A
cd ~/projects/project-a
python3 -m venv venv
source venv/bin/activate
pip install package==1.0

# Project B  
cd ~/projects/project-b
python3 -m venv venv
source venv/bin/activate
pip install package==2.0

# Both work! Isolated dependencies
```

### ACAD-GIS Virtual Environment
```bash
cd ~/projects/acad-gis

# Create venv (only once)
python3 -m venv venv

# Activate (every time you open terminal)
source venv/bin/activate

# Verify (prompt should show "(venv)")
(venv) josh_patheal@DESKTOP-F4AKB2B:~/projects/acad-gis$
```

### Managing Dependencies
```bash
# Install packages
pip install fastapi uvicorn psycopg2-binary

# Save to requirements.txt
pip freeze > requirements.txt

# Install from requirements.txt (fresh setup)
pip install -r requirements.txt
```

---

## VS Code Integration

### Open Project in VS Code
```bash
cd ~/projects/acad-gis
code .
```

**What happens:**
1. VS Code opens
2. Bottom-left shows "WSL: Ubuntu"
3. VS Code is now editing files in WSL
4. Terminal in VS Code is WSL bash

### VS Code Extensions for WSL

Auto-installed when opening WSL folder:
- **WSL:** Microsoft extension for remote development
- **Python:** Python language support
- **Pylance:** Type checking
- **GitLens:** Git visualization

---

## Common Issues & Solutions

### "wsl: command not found"

**Cause:** WSL not installed

**Solution:**
```powershell
# PowerShell (Administrator)
wsl --install
# Restart computer
```

### "Permission denied" accessing Windows files

**Cause:** Windows file permissions

**Solution:** Work in `~/projects/` instead of `/mnt/c/`

### Virtual environment not activating

**Symptom:** No `(venv)` in prompt

**Solution:**
```bash
cd ~/projects/acad-gis
source venv/bin/activate

# Verify
which python  # Should show: /home/josh_patheal/projects/acad-gis/venv/bin/python
```

### Git push asks for password

**Cause:** Using HTTPS instead of SSH

**Solution:** Change remote URL
```bash
git remote set-url origin git@github.com:Rtoony/acad-gis.git
```

---

## Daily Workflow

### Starting Work
```bash
# 1. Open Windows Terminal (auto-opens WSL)
# 2. Navigate to project
cd ~/projects/acad-gis

# 3. Activate virtual environment
source venv/bin/activate

# 4. Check git status
git status

# 5. Pull latest changes
git pull

# 6. Start coding!
code .
```

### Ending Work
```bash
# 1. Stage changes
git add .

# 2. Commit with message
git commit -m "Descriptive message about what you did"

# 3. Push to GitHub
git push

# 4. Deactivate venv (optional)
deactivate
```

---

## Key Takeaways

✅ **WSL gives you Linux on Windows** - Best of both worlds  
✅ **SSH keys authenticate with GitHub** - No passwords needed  
✅ **Virtual environments isolate dependencies** - Each project independent  
✅ **VS Code works seamlessly with WSL** - Edit Linux files from Windows GUI  
✅ **Git + GitHub = version control + backup** - Never lose work  

---

## Next Steps

1. **Read:** DEVELOPMENT_ENVIRONMENT.md (your specific project setup)
2. **Read:** GIT_WORKFLOW.md (how to use Git for daily work)
3. **Read:** DATABASE_CONNECTION.md (Supabase connection details)

---

**System Info:**
- **OS:** Windows 11
- **WSL:** Ubuntu 24.04
- **Terminal:** Windows Terminal
- **Python:** 3.12
- **Git:** 2.x
- **GitHub User:** Rtoony
