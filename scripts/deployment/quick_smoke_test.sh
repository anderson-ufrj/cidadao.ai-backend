#!/bin/bash
#
# Quick smoke tests for Railway production - Essential checks only
#
# Usage: ./scripts/deployment/quick_smoke_test.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROD_URL="${PROD_URL:-https://cidadao-api-production.up.railway.app}"
PASSED=0
FAILED=0

log_success() {
    echo -e "${GREEN}✅${NC} $1"
    ((PASSED++))
}

log_error() {
    echo -e "${RED}❌${NC} $1"
    ((FAILED++))
}

log_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

test_endpoint() {
    local name="$1"
    local endpoint="$2"
    local expected="${3:-200}"

    log_info "Testing: $name"
    status=$(curl -L -s -m 10 -w "%{http_code}" -o /dev/null "$PROD_URL$endpoint" 2>&1)

    if [ "$status" = "$expected" ]; then
        log_success "$name - Status: $status"
    else
        log_error "$name - Expected: $expected, Got: $status"
    fi
}

echo "==========================================="
echo "🧪 Quick Railway Production Smoke Tests"
echo "==========================================="
echo "Target: $PROD_URL"
echo "Time: $(date)"
echo "==========================================="
echo ""

# Critical tests only
log_info "--- Critical Health Checks ---"
test_endpoint "Health Check" "/health" 200
test_endpoint "API Docs" "/docs" 200
test_endpoint "Metrics" "/health/metrics" 200

log_info "--- Core API Endpoints ---"
test_endpoint "API Root" "/api/v1/" 200
test_endpoint "Agents List" "/api/v1/agents" 200

log_info "--- Federal APIs ---"
test_endpoint "IBGE States" "/api/v1/federal/ibge/states" 200

# Summary
echo ""
echo "==========================================="
echo "📊 Quick Test Summary"
echo "==========================================="
echo -e "Total: ${BLUE}$((PASSED + FAILED))${NC}"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo "==========================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILED test(s) failed${NC}"
    exit 1
fi
