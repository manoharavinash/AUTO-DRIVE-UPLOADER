#!/bin/bash
###############################################################################
# AUTO DRIVE UPLOADER - Quick Start Guide
# Run this to validate installation and start the app
###############################################################################

set -e

CYAN='\033[0;36m'
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
