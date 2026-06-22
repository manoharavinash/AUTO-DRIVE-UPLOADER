#!/bin/bash
###############################################################################
# AUTO DRIVE UPLOADER - Installation Script
# Automated setup for Termux and Linux environments
# Installs: apt dependencies, Python, RClone, and Python packages
###############################################################################

set -e  # Exit on any error#!/bin/bash
###############################################################################
# AUTO DRIVE UPLOADER - Installation Script
# Supports: Termux (Android) and Linux (Ubuntu/Debian)
###############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}========================================"
echo -e "  AUTO DRIVE UPLOADER — Setup Script"
echo -e "========================================${NC}"
echo ""

# ── Detect environment ────────────────────────────────────────────────────────
if [[ -d /data/data/com.termux ]]; then
    ENV="termux"
    PYTHON="python"
    echo -e "${GREEN}✓ Detected: Termux (Android)${NC}"
elif [[ "$(uname)" == "Linux" ]]; then
    ENV="linux"
    PYTHON="python3"
    echo -e "${GREEN}✓ Detected: Linux${NC}"
else
    echo -e "${RED}✗ Unsupported OS: $(uname)${NC}"
    exit 1
fi
echo ""

# ── Step 1: Update packages ───────────────────────────────────────────────────
echo -e "${CYAN}[1/5] Updating package manager...${NC}"
if [[ "$ENV" == "termux" ]]; then
    apt update -y && apt upgrade -y
else
    sudo apt-get update -y
fi
echo -e "${GREEN}✓ Done${NC}\n"

# ── Step 2: Install system dependencies ──────────────────────────────────────
echo -e "${CYAN}[2/5] Installing Python, git, curl...${NC}"
if [[ "$ENV" == "termux" ]]; then
    apt install -y python git curl
    # Termux ships python3 as 'python'; create alias if missing
    if ! command -v python3 &>/dev/null; then
        ln -sf "$(command -v python)" "$PREFIX/bin/python3" 2>/dev/null || true
    fi
else
    sudo apt-get install -y python3 python3-pip git curl
fi
echo -e "${GREEN}✓ Done${NC}\n"

# ── Step 3: Install RClone ────────────────────────────────────────────────────
echo -e "${CYAN}[3/5] Installing RClone...${NC}"
if command -v rclone &>/dev/null; then
    echo -e "${GREEN}✓ Already installed: $(rclone version | head -n1)${NC}"
else
    if [[ "$ENV" == "termux" ]]; then
        apt install -y rclone
    else
        curl https://rclone.org/install.sh | sudo bash
    fi
    echo -e "${GREEN}✓ RClone installed${NC}"
fi
echo ""

# ── Step 4: Install Python packages ──────────────────────────────────────────
echo -e "${CYAN}[4/5] Installing Python packages...${NC}"
if [[ "$ENV" == "termux" ]]; then
    # Termux uses system Python; no --user needed, no venv issues
    pip install --upgrade pip
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    # Use --break-system-packages on newer Debian/Ubuntu that enforce PEP 668
    $PYTHON -m pip install --upgrade pip --break-system-packages 2>/dev/null \
        || $PYTHON -m pip install --upgrade pip
    $PYTHON -m pip install -r "$SCRIPT_DIR/requirements.txt" --break-system-packages 2>/dev/null \
        || $PYTHON -m pip install -r "$SCRIPT_DIR/requirements.txt"
fi
echo -e "${GREEN}✓ Done${NC}\n"

# ── Step 5: Check RClone remote ───────────────────────────────────────────────
echo -e "${CYAN}[5/5] Checking RClone remote...${NC}"
if rclone listremotes 2>/dev/null | grep -q "google auto photo"; then
    echo -e "${GREEN}✓ Remote 'google auto photo' is configured${NC}"
else
    echo -e "${YELLOW}⚠  Remote not found. Configure it now:${NC}"
    echo -e "${CYAN}      rclone config${NC}"
    echo -e "${YELLOW}   Name it exactly: google auto photo"
    echo -e "   Type: Google Drive"
    echo -e "   Complete OAuth in browser${NC}"
fi
echo ""

# ── Make scripts executable ───────────────────────────────────────────────────
chmod +x "$SCRIPT_DIR/install.sh" "$SCRIPT_DIR/start.sh" 2>/dev/null || true

echo -e "${CYAN}========================================"
echo -e "${GREEN}✓ Installation complete!${NC}"
echo -e "${CYAN}========================================"
echo ""
echo -e "  To launch:"
echo -e "${YELLOW}    bash start.sh${NC}"
echo -e "  or"
echo -e "${YELLOW}    $PYTHON upload.py${NC}"
echo ""

exit 0


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
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "linux-android"* ]]; then
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
    apt install -y python git curl
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

# Install Python packages
if [[ "$ENV" == "termux" ]]; then
    python -m pip install --upgrade pip
    python -m pip install -r "$SCRIPT_DIR/requirements.txt"
else
    python3 -m pip install --upgrade pip
    python3 -m pip install -r "$SCRIPT_DIR/requirements.txt"
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
