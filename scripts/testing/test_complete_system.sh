#!/bin/bash

API_URL="https://cidadao-api-production.up.railway.app"

echo "🎯 TESTE COMPLETO DO SISTEMA CIDADÃO.AI"
echo "========================================"
echo "API: $API_URL"
echo "Data: $(date)"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: Health Check
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 1: Health Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
HEALTH=$(curl -s "${API_URL}/health/")
STATUS=$(echo "$HEALTH" | jq -r '.status')

if [ "$STATUS" == "ok" ]; then
  echo -e "${GREEN}✅ PASS: API is healthy${NC}"
  echo "$HEALTH" | jq '.'
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${RED}❌ FAIL: API is not healthy${NC}"
  echo "$HEALTH" | jq '.'
  TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 2: Database Configuration
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 2: Database Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
DB_CONFIG=$(curl -s "${API_URL}/api/v1/debug/database-config")
DB_TYPE=$(echo "$DB_CONFIG" | jq -r '.database.database_type')
TABLE_EXISTS=$(echo "$DB_CONFIG" | jq -r '.tables.investigations_exists')
INV_COUNT=$(echo "$DB_CONFIG" | jq -r '.investigations.total_count')

if [ "$DB_TYPE" == "PostgreSQL" ] && [ "$TABLE_EXISTS" == "true" ]; then
  echo -e "${GREEN}✅ PASS: PostgreSQL connected, table exists${NC}"
  echo "Database: $DB_TYPE"
  echo "Investigations table: $TABLE_EXISTS"
  echo "Total investigations: $INV_COUNT"
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${RED}❌ FAIL: Database issues${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 3: Anita Agent (Analysis)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 3: Anita Agent - Analysis${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
ANITA_RESPONSE=$(curl -sX POST "${API_URL}/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analisar anomalias em licitações municipais",
    "session_id": "test_complete_anita"
  }')

ANITA_AGENT=$(echo "$ANITA_RESPONSE" | jq -r '.agent_name')
ANITA_MESSAGE=$(echo "$ANITA_RESPONSE" | jq -r '.message')

if [[ "$ANITA_AGENT" == "Anita"* ]] && [[ "$ANITA_MESSAGE" != *"error"* ]]; then
  echo -e "${GREEN}✅ PASS: Anita responded successfully${NC}"
  echo "Agent: $ANITA_AGENT"
  echo "Message preview: ${ANITA_MESSAGE:0:100}..."
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${RED}❌ FAIL: Anita error${NC}"
  echo "$ANITA_RESPONSE" | jq '.'
  TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 4: Zumbi Agent (Investigation) + Persistence
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 4: Zumbi Agent - Investigation + Persistence${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Get initial count
INITIAL_COUNT=$(curl -s "${API_URL}/api/v1/debug/database-config" | jq -r '.investigations.total_count')
echo "Initial investigation count: $INITIAL_COUNT"

# Create investigation
TIMESTAMP=$(date +%s)
ZUMBI_RESPONSE=$(curl -sX POST "${API_URL}/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Investigar contratos de fornecedores com valores suspeitos teste_${TIMESTAMP}\",
    \"session_id\": \"test_complete_zumbi_${TIMESTAMP}\"
  }")

ZUMBI_AGENT=$(echo "$ZUMBI_RESPONSE" | jq -r '.agent_name')
ZUMBI_MESSAGE=$(echo "$ZUMBI_RESPONSE" | jq -r '.message')

echo "Agent: $ZUMBI_AGENT"
echo "Message preview: ${ZUMBI_MESSAGE:0:150}..."

# Wait for processing
sleep 5

# Check if persisted
FINAL_COUNT=$(curl -s "${API_URL}/api/v1/debug/database-config" | jq -r '.investigations.total_count')
echo "Final investigation count: $FINAL_COUNT"

if [[ "$ZUMBI_AGENT" == "Zumbi"* ]] && [ "$FINAL_COUNT" -gt "$INITIAL_COUNT" ]; then
  echo -e "${GREEN}✅ PASS: Zumbi investigation created AND persisted${NC}"
  DIFF=$((FINAL_COUNT - INITIAL_COUNT))
  echo "New investigations: +$DIFF"
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${RED}❌ FAIL: Investigation not persisted${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 5: Recent Investigations
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 5: Recent Investigations Query${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
RECENT=$(curl -s "${API_URL}/api/v1/debug/database-config" | jq '.investigations.recent_investigations')
RECENT_COUNT=$(echo "$RECENT" | jq 'length')

if [ "$RECENT_COUNT" -gt 0 ]; then
  echo -e "${GREEN}✅ PASS: Can query recent investigations${NC}"
  echo "Recent investigations found: $RECENT_COUNT"
  echo ""
  echo "Latest 3 investigations:"
  echo "$RECENT" | jq '.[:3] | .[] | {id, status, created_at}'
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${RED}❌ FAIL: No investigations found${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 6: Chat Agent List
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 6: Chat Agents List${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
AGENTS=$(curl -s "${API_URL}/api/v1/chat/agents")
AGENTS_COUNT=$(echo "$AGENTS" | jq 'length')

if [ "$AGENTS_COUNT" -gt 0 ]; then
  echo -e "${GREEN}✅ PASS: Chat agents available${NC}"
  echo "Available agents: $AGENTS_COUNT"
  echo ""
  echo "Agent list:"
  echo "$AGENTS" | jq '.[] | {id, name, role, description}'
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${RED}❌ FAIL: No agents available${NC}"
  echo "$AGENTS" | jq '.'
  TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# Test 7: Maritaca Direct Chat
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 7: Maritaca Direct Chat${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
MARITACA=$(curl -sX POST "${API_URL}/api/v1/chat/direct/maritaca" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Olá, teste"}],
    "model": "sabiazinho-3"
  }')

MARITACA_CONTENT=$(echo "$MARITACA" | jq -r '.content // empty')

if [ -n "$MARITACA_CONTENT" ]; then
  echo -e "${GREEN}✅ PASS: Maritaca direct chat working${NC}"
  echo "Response: ${MARITACA_CONTENT:0:100}..."
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${YELLOW}⚠️  SKIP: Maritaca endpoint may not be configured${NC}"
  echo "$MARITACA" | jq '.'
fi
echo ""

# Final Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 FINAL TEST SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Total tests run: $((TESTS_PASSED + TESTS_FAILED))"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${GREEN}🎉 ALL TESTS PASSED! System fully operational!${NC}"
  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  exit 0
else
  echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${RED}❌ Some tests failed. Review errors above.${NC}"
  echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  exit 1
fi
