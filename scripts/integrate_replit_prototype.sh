#!/bin/bash
# Integration helper script for bringing Replit prototypes into acad-gis

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Replit Prototype Integration Helper${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if branch name provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: ./scripts/integrate_replit_prototype.sh <branch-name> [destination]${NC}"
    echo ""
    echo "Examples:"
    echo "  ./scripts/integrate_replit_prototype.sh replit-prototype-survey-tool"
    echo "  ./scripts/integrate_replit_prototype.sh replit-prototype-bmp-editor prototypes"
    echo ""
    echo -e "${YELLOW}Available Replit branches:${NC}"
    git branch -r | grep "origin/replit-" | sed 's/origin\///' || echo "  No replit branches found yet"
    exit 1
fi

BRANCH_NAME=$1
DESTINATION=${2:-"prototypes"}  # Default to prototypes folder

echo -e "${GREEN}Step 1: Fetching branch from GitHub...${NC}"
git fetch origin

echo -e "${GREEN}Step 2: Checking out branch ${BRANCH_NAME}...${NC}"
if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
    git checkout "${BRANCH_NAME}"
else
    git checkout -b "${BRANCH_NAME}" "origin/${BRANCH_NAME}"
fi

echo -e "${GREEN}Step 3: Showing recent changes...${NC}"
git log --oneline -5

echo ""
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Branch ${BRANCH_NAME} is now active${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""
echo "You can now use Claude Code to:"
echo "  1. Review the code quality"
echo "  2. Refactor to match acad-gis patterns"
echo "  3. Add tests (see QUICK_START_TESTING.md)"
echo "  4. Update documentation"
echo "  5. Integrate into ${DESTINATION}/"
echo ""
echo "When ready to commit and push:"
echo "  git add ."
echo "  git commit -m 'Integration: [description]'"
echo "  git push origin ${BRANCH_NAME}"
echo ""
echo "To merge to main when ready:"
echo "  git checkout main"
echo "  git merge ${BRANCH_NAME}"
echo "  git push origin main"
