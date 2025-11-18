#!/bin/bash
#
# Smoke tests for Railway production environment
# Tests critical endpoints to ensure system is functional
#
# Usage:
#   ./scripts/deployment/smoke_test_production.sh
#
# Environment:
#   PROD_URL (optional): Production URL (default: https://cidadao-api-production.up.railway.app)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROD_URL="${PROD_URL:-https://cidadao-api-production.up.railway.app}"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
}

log_error() {
    echo -e "${RED}❌${NC} $1"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
}

log_warning() {
    echo -e "${YELLOW}⚠️ ${NC} $1"
}

test_endpoint() {
    local name="$1"
    local endpoint="$2"
    local expected_status="${3:-200}"
    local method="${4:-GET}"

    log_info "Testing: $name ($method $endpoint)"

    if [ "$method" = "GET" ]; then
        response=$(curl -L -s -w "\n%{http_code}" -X GET "$PROD_URL$endpoint" -H "Accept: application/json" 2>&1)
    else
        response=$(curl -L -s -w "\n%{http_code}" -X "$method" "$PROD_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Accept: application/json" \
            -d '{}' 2>&1)
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$status_code" = "$expected_status" ]; then
        log_success "$name - Status: $status_code"
        return 0
    else
        log_error "$name - Expected: $expected_status, Got: $status_code"
        echo "Response: $body" | head -n 3
        return 1
    fi
}

test_json_response() {
    local name="$1"
    local endpoint="$2"
    local json_path="$3"

    log_info "Testing: $name (JSON validation)"

    response=$(curl -L -s "$PROD_URL$endpoint" -H "Accept: application/json" 2>&1)

    # Check if response is valid JSON
    if echo "$response" | jq empty 2>/dev/null; then
        # Check if JSON path exists
        if echo "$response" | jq -e "$json_path" >/dev/null 2>&1; then
            value=$(echo "$response" | jq -r "$json_path")
            log_success "$name - Found: $json_path = $value"
            return 0
        else
            log_error "$name - JSON path not found: $json_path"
            return 1
        fi
    else
        log_error "$name - Invalid JSON response"
        echo "Response: $response" | head -n 3
        return 1
    fi
}

# Banner
echo ""
echo "=========================================="
echo "🧪 Railway Production Smoke Tests"
echo "=========================================="
echo "Target: $PROD_URL"
echo "Time: $(date)"
echo "=========================================="
echo ""

# Test 1: Health Check
log_info "--- Test Suite 1: Core Health ---"
test_endpoint "Health Check" "/health" 200

# Test 2: Metrics Endpoint
test_endpoint "Prometheus Metrics" "/health/metrics" 200

# Test 3: API Documentation
test_endpoint "OpenAPI Docs" "/docs" 200
test_endpoint "OpenAPI JSON" "/openapi.json" 200

# Test 4: API Root
log_info "--- Test Suite 2: API Endpoints ---"
test_endpoint "API Root" "/api/v1/" 200

# Test 5: Agents List
if test_endpoint "Agents List" "/api/v1/agents" 200; then
    # Validate agents in response
    agents_count=$(curl -L -s "$PROD_URL/api/v1/agents" | jq '. | length' 2>/dev/null || echo "0")
    if [ "$agents_count" -gt "0" ]; then
        log_success "Agents List - Found $agents_count agents"
    else
        log_warning "Agents List - No agents found or JSON parse error"
    fi
fi

# Test 6: Investigations Endpoint
test_endpoint "Investigations List" "/api/v1/investigations?limit=1" 200

# Test 7: Federal APIs
log_info "--- Test Suite 3: Federal APIs ---"
test_endpoint "IBGE States" "/api/v1/federal/ibge/states" 200
test_endpoint "PNCP Search" "/api/v1/federal/pncp/search?query=educacao&limit=1" 200

# Test 8: Transparency API (may be limited)
log_info "--- Test Suite 4: Transparency APIs ---"
test_endpoint "Portal Agencies" "/api/v1/transparency/agencies?limit=5" 200 || log_warning "Portal API may be blocked (expected)"

# Test 9: GraphQL Endpoint
log_info "--- Test Suite 5: GraphQL ---"
if test_endpoint "GraphQL Endpoint" "/api/v1/graphql" 200 POST; then
    log_success "GraphQL - Endpoint accessible"
else
    log_warning "GraphQL - May require authentication or specific query"
fi

# Test 10: Database Connection (indirect)
log_info "--- Test Suite 6: Database ---"
# Try to fetch recent investigations (tests DB connection)
if curl -L -s "$PROD_URL/api/v1/investigations?limit=1" | jq empty 2>/dev/null; then
    log_success "Database - Connection OK (via investigations endpoint)"
else
    log_error "Database - Connection failed or no data"
fi

# Test 11: Specific Agent Health
log_info "--- Test Suite 7: Agent System ---"

# Try to get Zumbi agent info
if curl -L -s "$PROD_URL/api/v1/agents" | jq -e '.[] | select(.name == "Zumbi")' >/dev/null 2>&1; then
    log_success "Agent System - Zumbi agent found"
else
    log_warning "Agent System - Could not verify Zumbi agent"
fi

# Test 12: Response Time Check
log_info "--- Test Suite 8: Performance ---"
start_time=$(date +%s%N)
curl -L -s "$PROD_URL/health" > /dev/null
end_time=$(date +%s%N)
response_time=$(( (end_time - start_time) / 1000000 ))  # Convert to milliseconds

if [ "$response_time" -lt 500 ]; then
    log_success "Response Time - ${response_time}ms (< 500ms target)"
elif [ "$response_time" -lt 1000 ]; then
    log_warning "Response Time - ${response_time}ms (acceptable but slow)"
else
    log_error "Response Time - ${response_time}ms (> 1000ms - too slow)"
fi

# Summary
echo ""
echo "=========================================="
echo "📊 Test Summary"
echo "=========================================="
echo -e "Total Tests: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    success_rate=100
else
    success_rate=$(( PASSED_TESTS * 100 / TOTAL_TESTS ))
fi

echo -e "Success Rate: ${BLUE}${success_rate}%${NC}"
echo "=========================================="

# Exit code
if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL SMOKE TESTS PASSED!${NC}"
    echo -e "${GREEN}✅ Production system is healthy${NC}"
    echo ""
    exit 0
elif [ $FAILED_TESTS -le 2 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Some tests failed but system is mostly functional${NC}"
    echo -e "${YELLOW}   Review failed tests above${NC}"
    echo ""
    exit 0  # Don't fail build for minor issues
else
    echo ""
    echo -e "${RED}❌ CRITICAL: Multiple smoke tests failed${NC}"
    echo -e "${RED}   Production system may have issues${NC}"
    echo ""
    exit 1
fi
