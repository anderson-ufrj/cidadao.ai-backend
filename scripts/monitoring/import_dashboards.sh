#!/bin/bash
# Import Grafana Dashboards Script
# Usage: ./import_dashboards.sh [grafana_url] [api_key]

set -e

# Configuration
GRAFANA_URL="${1:-http://localhost:3000}"
API_KEY="${2:-}"
DASHBOARDS_DIR="$(cd "$(dirname "$0")/../../monitoring/grafana/dashboards" && pwd)"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Cidadão.AI Dashboard Import Utility${NC}"
echo -e "${BLUE}======================================${NC}"
echo

# Check if API key is provided
if [ -z "$API_KEY" ]; then
    echo -e "${YELLOW}Warning: No API key provided${NC}"
    echo "Usage: $0 [grafana_url] [api_key]"
    echo
    echo "Attempting to use default admin credentials..."
    AUTH_HEADER="Authorization: Basic $(echo -n 'admin:admin' | base64)"
else
    AUTH_HEADER="Authorization: Bearer $API_KEY"
fi

# Check if dashboards directory exists
if [ ! -d "$DASHBOARDS_DIR" ]; then
    echo -e "${RED}Error: Dashboards directory not found: $DASHBOARDS_DIR${NC}"
    exit 1
fi

# List of new dashboard files (numbered)
DASHBOARD_FILES=(
    "1-production-overview.json"
    "2-agents-performance.json"
    "3-investigations.json"
    "4-anomaly-detection.json"
    "5-api-performance.json"
    "6-infrastructure.json"
)

echo -e "${BLUE}Grafana URL:${NC} $GRAFANA_URL"
echo -e "${BLUE}Dashboards Directory:${NC} $DASHBOARDS_DIR"
echo

# Test Grafana connection
echo -e "${YELLOW}Testing Grafana connection...${NC}"
if ! curl -s -f -H "$AUTH_HEADER" "$GRAFANA_URL/api/health" > /dev/null 2>&1; then
    echo -e "${RED}Error: Cannot connect to Grafana at $GRAFANA_URL${NC}"
    echo "Please check:"
    echo "  1. Grafana is running"
    echo "  2. URL is correct"
    echo "  3. API key is valid (if provided)"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Grafana${NC}"
echo

# Function to import a single dashboard
import_dashboard() {
    local file=$1
    local filepath="$DASHBOARDS_DIR/$file"

    if [ ! -f "$filepath" ]; then
        echo -e "${YELLOW}  Skipping: File not found${NC}"
        return 1
    fi

    # Read dashboard JSON and wrap it for import
    local dashboard_json=$(cat "$filepath")
    local import_json=$(cat <<EOF
{
  "dashboard": $dashboard_json,
  "overwrite": true,
  "message": "Imported via script"
}
EOF
)

    # Import dashboard
    local response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -H "$AUTH_HEADER" \
        -d "$import_json" \
        "$GRAFANA_URL/api/dashboards/db")

    local http_code=$(echo "$response" | tail -n1)
    local response_body=$(echo "$response" | head -n-1)

    if [ "$http_code" -eq 200 ]; then
        local dashboard_url=$(echo "$response_body" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}  ✓ Imported successfully${NC}"
        if [ -n "$dashboard_url" ]; then
            echo -e "    URL: ${GRAFANA_URL}${dashboard_url}"
        fi
        return 0
    else
        echo -e "${RED}  ✗ Import failed (HTTP $http_code)${NC}"
        echo "$response_body" | grep -o '"message":"[^"]*"' | cut -d'"' -f4
        return 1
    fi
}

# Import all dashboards
echo -e "${BLUE}Importing Cidadão.AI Dashboards...${NC}"
echo

success_count=0
fail_count=0

for dashboard_file in "${DASHBOARD_FILES[@]}"; do
    dashboard_name=$(basename "$dashboard_file" .json)
    echo -e "${YELLOW}[$((success_count + fail_count + 1))/${#DASHBOARD_FILES[@]}]${NC} Importing: ${dashboard_name}"

    if import_dashboard "$dashboard_file"; then
        ((success_count++))
    else
        ((fail_count++))
    fi
    echo
done

# Summary
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Import Summary${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}Successfully imported:${NC} $success_count dashboard(s)"
if [ $fail_count -gt 0 ]; then
    echo -e "${RED}Failed to import:${NC} $fail_count dashboard(s)"
fi
echo

if [ $success_count -eq ${#DASHBOARD_FILES[@]} ]; then
    echo -e "${GREEN}✓ All dashboards imported successfully!${NC}"
    echo
    echo "Next steps:"
    echo "  1. Open Grafana: $GRAFANA_URL"
    echo "  2. Navigate to Dashboards → Browse"
    echo "  3. Start with: 'Cidadão.AI - Production Overview'"
    exit 0
else
    echo -e "${YELLOW}Some dashboards failed to import${NC}"
    echo "Please check the error messages above"
    exit 1
fi
