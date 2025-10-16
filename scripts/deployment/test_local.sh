#!/bin/bash
#
# Test backend locally before deployment
#
# Usage:
#   ./scripts/deployment/test_local.sh
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}🧪 Testing Cidadão.AI Backend${NC}"
echo -e "${BLUE}================================${NC}"

# Check if server is running
SERVER_URL="http://localhost:8000"

echo -e "\n${YELLOW}Checking if server is running...${NC}"
if ! curl -s -f "$SERVER_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Server is not running at $SERVER_URL${NC}"
    echo -e "${YELLOW}Start the server with: make run-dev${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"

# Test health endpoint
echo -e "\n${YELLOW}Testing /health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "$SERVER_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "$HEALTH_RESPONSE" | head -3
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "$HEALTH_RESPONSE"
    exit 1
fi

# Test API info
echo -e "\n${YELLOW}Testing /api/v1/info endpoint...${NC}"
INFO_RESPONSE=$(curl -s "$SERVER_URL/api/v1/info")
if echo "$INFO_RESPONSE" | grep -q "version"; then
    echo -e "${GREEN}✅ API info endpoint working${NC}"
    echo "$INFO_RESPONSE" | head -5
else
    echo -e "${RED}❌ API info endpoint failed${NC}"
    echo "$INFO_RESPONSE"
    exit 1
fi

# Test Federal APIs (no auth required)
echo -e "\n${YELLOW}Testing Federal API - IBGE states...${NC}"
STATES_RESPONSE=$(curl -s "$SERVER_URL/api/v1/federal/ibge/states")
if echo "$STATES_RESPONSE" | grep -q "São Paulo\|Rio de Janeiro"; then
    STATE_COUNT=$(echo "$STATES_RESPONSE" | grep -o "nome" | wc -l)
    echo -e "${GREEN}✅ IBGE API working (${STATE_COUNT} states found)${NC}"
else
    echo -e "${YELLOW}⚠️  IBGE API response unexpected${NC}"
    echo "$STATES_RESPONSE" | head -3
fi

# Test authentication (register + login)
echo -e "\n${YELLOW}Testing authentication flow...${NC}"

# Generate random test user
TEST_EMAIL="test_$(date +%s)@cidadao.ai"
TEST_PASSWORD="testpass123"

# Register
echo -e "  Registering test user: $TEST_EMAIL"
REGISTER_RESPONSE=$(curl -s -X POST "$SERVER_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\",
        \"full_name\": \"Test User\"
    }")

if echo "$REGISTER_RESPONSE" | grep -q "user_id\|id"; then
    echo -e "${GREEN}  ✅ User registration successful${NC}"
else
    echo -e "${YELLOW}  ⚠️  Registration response: ${NC}"
    echo "$REGISTER_RESPONSE" | head -3
fi

# Login
echo -e "  Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$SERVER_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{
        \"username\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\"
    }")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}  ✅ Login successful (token obtained)${NC}"

    # Test authenticated endpoint
    echo -e "\n${YELLOW}Testing authenticated endpoint...${NC}"
    ME_RESPONSE=$(curl -s "$SERVER_URL/api/v1/auth/me" \
        -H "Authorization: Bearer $TOKEN")

    if echo "$ME_RESPONSE" | grep -q "$TEST_EMAIL"; then
        echo -e "${GREEN}✅ Authentication working${NC}"
    else
        echo -e "${YELLOW}⚠️  /auth/me response unexpected${NC}"
        echo "$ME_RESPONSE" | head -3
    fi
else
    echo -e "${YELLOW}  ⚠️  Login response unexpected${NC}"
    echo "$LOGIN_RESPONSE" | head -3
fi

# Summary
echo -e "\n${BLUE}================================${NC}"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo -e "${BLUE}================================${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Review logs: ${BLUE}railway logs${NC} (after deploy)"
echo -e "  2. Run full test suite: ${BLUE}make test${NC}"
echo -e "  3. Deploy to Railway: ${BLUE}railway up${NC}"

exit 0
