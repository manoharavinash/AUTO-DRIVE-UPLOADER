#!/bin/bash
###############################################################################
# AUTO DRIVE UPLOADER - Installation Script
# Automated setup for Termux and Linux environments
# Installs: apt dependencies, Python, RClone, and Python packages
###############################################################################

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}AUTO DRIVE UPLOADER - Setup Script${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Detect environment
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [[ -d /data/data/com.termux ]]; then
        ENV="termux"
        echo -e "${GREEN}✓ Detected: Termux${NC}"
    else
        ENV="linux"
        echo -e "${GREEN}✓ Detected: Linux${NC}"
    fi
else
    echo -e "${RED}✗ Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}Step 1: Updating package manager...${NC}"

if [[ "$ENV" == "termux" ]]; then
    apt update -y
    apt upgrade -y
else
    sudo apt update -y
    sudo apt upgrade -y
fi

echo -e "${GREEN}✓ Package manager updated${NC}"
echo ""

echo -e "${CYAN}Step 2: Installing Python and dependencies...${NC}"

if [[ "$ENV" == "termux" ]]; then
    apt install -y python python-pip git curl
else
    sudo apt install -y python3 python3-pip git curl
fi

echo -e "${GREEN}✓ Python installed${NC}"
echo ""

echo -e "${CYAN}Step 3: Installing RClone...${NC}"

# Check if rclone is already installed
if command -v rclone &> /dev/null; then
    RCLONE_VERSION=$(rclone version | head -n1)
    echo -e "${GREEN}✓ RClone already installed: $RCLONE_VERSION${NC}"
else
    # Install rclone
    if [[ "$ENV" == "termux" ]]; then
        apt install -y rclone
    else
        # For Linux, use official script
        curl https://rclone.org/install.sh | sudo bash
    fi
    echo -e "${GREEN}✓ RClone installed${NC}"
fi

echo ""

echo -e "${CYAN}Step 4: Installing Python packages...${NC}"

# Upgrade pip
if [[ "$ENV" == "termux" ]]; then
    pip install --upgrade pip
else
    pip3 install --upgrade pip
fi

# Install requirements
if [[ "$ENV" == "termux" ]]; then
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
fi

echo -e "${GREEN}✓ Python packages installed${NC}"
echo ""

echo -e "${CYAN}Step 5: Configuring RClone...${NC}"

if ! rclone listremotes | grep -q "google auto photo"; then
    echo -e "${YELLOW}⚠ Remote 'google auto photo' not configured${NC}"
    echo -e "${YELLOW}Run the following command to configure:${NC}"
    echo -e "${CYAN}  rclone config${NC}"
    echo -e "${YELLOW}Then create a new remote with name: 'google auto photo'${NC}"
else
    echo -e "${GREEN}✓ Remote 'google auto photo' found${NC}"
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}✓ Installation complete!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${CYAN}To start the application:${NC}"
echo -e "${YELLOW}  python upload.py${NC}"
echo ""

exit 0
