#!/usr/bin/env bash
set -euo pipefail

# Color codes for output
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Set service account credentials if available
SA_KEY_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/sa/key.json"
if [ -f "$SA_KEY_PATH" ]; then
    export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$SA_KEY_PATH}"
    echo -e "${GREEN}Using service account: $SA_KEY_PATH${NC}"
fi

echo -e "${YELLOW}=== IsPilot API Local Development Setup ===${NC}"

# Check if venv exists
VENV_PATH=".venv"
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3.12 -m venv "$VENV_PATH"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate venv
echo -e "${YELLOW}Activating virtual environment...${NC}"
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
else
    # Windows path
    source "$VENV_PATH/Scripts/activate"
fi
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install/upgrade dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env from template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env created from template${NC}"
        echo -e "${YELLOW}Please update .env with your local configuration${NC}"
    fi
fi

# Print configuration instructions
echo ""
echo -e "${YELLOW}=== Configuration Required ===${NC}"
echo ""
echo "Set these environment variables in .env:"
echo "  GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json"
echo "  GOOGLE_CLOUD_PROJECT=corp-stro-salesinventory-prod"
echo "  GOOGLE_CLOUD_LOCATION=us-central1"
echo "  VERTEX_PROJECT_ID=corp-stro-salesinventory-prod"
echo "  VERTEX_LOCATION=us-central1"
echo "  VERTEX_ENGINE_ID=5375474415045705728"
echo "  ISPILOT_API_KEY=your-test-api-key"
echo "  SESSION_TIMEOUT_HOURS=8"
echo ""

# Load environment if .env exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading environment from .env...${NC}"
    export $(grep -v '^#' .env | xargs)
fi

# Verify required variables
REQUIRED_VARS=(
    "GOOGLE_CLOUD_PROJECT"
    "GOOGLE_CLOUD_LOCATION"
    "VERTEX_PROJECT_ID"
    "VERTEX_LOCATION"
    "VERTEX_ENGINE_ID"
    "ISPILOT_API_KEY"
)

MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warning: Missing environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "The application may fail to start without these variables."
fi

# Start the application
echo ""
echo -e "${GREEN}=== Starting IsPilot API ===${NC}"
echo ""
echo "Server running on: http://localhost:8080"
echo "Docs available at: http://localhost:8080/docs"
echo "Health check: http://localhost:8080/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
