#!/bin/bash
###############################################################################
# AUTO DRIVE UPLOADER - Quick Start Guide
# Run this to validate installation and start the app
###############################################################################

set -e

CYAN='\033[0;36m'#!/bin/bash
###############################################################################
# AUTO DRIVE UPLOADER - Quick Start / Pre-flight Check
###############################################################################

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

echo -e "${CYAN}AUTO DRIVE UPLOADER — Pre-flight Check${NC}"
echo ""

# ── Detect Python command ─────────────────────────────────────────────────────
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo -e "${RED}✗ Python not found. Run: bash install.sh${NC}"
    exit 1
fi
PYTHON_VER=$($PYTHON --version 2>&1)
echo -e "${GREEN}✓ $PYTHON_VER${NC}"

# ── Check RClone ──────────────────────────────────────────────────────────────
if command -v rclone &>/dev/null; then
    RCLONE_VER=$(rclone version 2>/dev/null | head -n1)
    echo -e "${GREEN}✓ $RCLONE_VER${NC}"
else
    echo -e "${RED}✗ RClone not found. Run: bash install.sh${NC}"
    ERRORS=$((ERRORS + 1))
fi

# ── Check rich library ────────────────────────────────────────────────────────
if $PYTHON -c "import rich" 2>/dev/null; then
    echo -e "${GREEN}✓ rich library OK${NC}"
else
    echo -e "${RED}✗ rich not installed. Run: bash install.sh${NC}"
    ERRORS=$((ERRORS + 1))
fi

# ── Check RClone remote ───────────────────────────────────────────────────────
if command -v rclone &>/dev/null; then
    if rclone listremotes 2>/dev/null | grep -q "google auto photo"; then
        echo -e "${GREEN}✓ Remote 'google auto photo' configured${NC}"
    else
        echo -e "${YELLOW}⚠  Remote 'google auto photo' not found${NC}"
        echo -e "${YELLOW}   Run: rclone config   (then name it 'google auto photo')${NC}"
        # Not a hard error — app will surface this at runtime
    fi
fi

echo ""

if [[ $ERRORS -gt 0 ]]; then
    echo -e "${RED}✗ $ERRORS issue(s) found. Run: bash install.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All checks passed — starting app...${NC}"
echo ""

exec $PYTHON upload.py

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}AUTO DRIVE UPLOADER - Quick Start${NC}"
echo ""

# Check Python
echo -e "${CYAN}Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✓ $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}✗ Python3 not found. Run: bash install.sh${NC}"
    exit 1
fi

# Check RClone
echo -e "${CYAN}Checking RClone...${NC}"
if command -v rclone &> /dev/null; then
    RCLONE_VERSION=$(rclone version | head -n1)
    echo -e "${GREEN}✓ $RCLONE_VERSION found${NC}"
else
    echo -e "${RED}✗ RClone not found. Run: bash install.sh${NC}"
    exit 1
fi

# Check dependencies
echo -e "${CYAN}Checking Python dependencies...${NC}"
if python3 -c "import rich" 2>/dev/null; then
    echo -e "${GREEN}✓ rich library installed${NC}"
else
    echo -e "${RED}✗ Dependencies missing. Run: bash install.sh${NC}"
    exit 1
fi

# Check remote
echo -e "${CYAN}Checking RClone configuration...${NC}"
if rclone listremotes | grep -q "google auto photo"; then
    echo -e "${GREEN}✓ Remote 'google auto photo' configured${NC}"
else
    echo -e "${RED}⚠ Remote not configured. Run: rclone config${NC}"
fi

echo ""
echo -e "${GREEN}✓ All checks passed!${NC}"
echo ""
echo -e "${CYAN}Starting application...${NC}"
echo ""

python3 upload.py
