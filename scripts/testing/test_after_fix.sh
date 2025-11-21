#!/bin/bash

# Teste rápido após correção do IP Whitelist
BASE_URL="https://cidadao-api-production.up.railway.app"

echo "=========================================="
echo "🧪 TESTANDO APÓS CORREÇÃO DO IP WHITELIST"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Aguarda deploy
echo "⏳ Aguardando 30 segundos para deploy..."
sleep 30

echo ""
echo "1. TESTE BÁSICO"
echo "--------------"

# Health check
echo -n "Health Check: "
status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health/")
if [ "$status" == "200" ]; then
    echo -e "${GREEN}✅ OK ($status)${NC}"
else
    echo -e "${RED}❌ FALHOU ($status)${NC}"
fi

echo ""
echo "2. TESTE DE AGENTES"
echo "-------------------"

# Testa 3 agentes principais
agents=("zumbi" "anita" "tiradentes")
for agent in "${agents[@]}"; do
    echo -n "Agente $agent: "
    data='{"query":"Teste rápido","context":{},"options":{}}'
    status=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$data" \
        "$BASE_URL/api/v1/agents/$agent")

    if [ "$status" == "200" ]; then
        echo -e "${GREEN}✅ OK ($status)${NC}"
    else
        echo -e "${RED}❌ FALHOU ($status)${NC}"
    fi
done

echo ""
echo "3. TESTE DE SSE STREAMING"
echo "-------------------------"

echo -n "Chat SSE: "
data='{"message":"Teste SSE","session_id":"test-sse"}'
response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: text/event-stream" \
    -d "$data" \
    --max-time 3 \
    "$BASE_URL/api/v1/chat/stream" 2>/dev/null | head -n5)

if echo "$response" | grep -q "event:" || echo "$response" | grep -q "data:"; then
    echo -e "${GREEN}✅ SSE funcionando${NC}"
elif echo "$response" | grep -q "Access denied"; then
    echo -e "${RED}❌ Ainda bloqueado (403)${NC}"
else
    echo -e "${YELLOW}⚠️  Resposta não clara${NC}"
fi

echo ""
echo "4. TESTE DE CORS"
echo "----------------"

echo -n "CORS Headers: "
cors_headers=$(curl -s -I -X OPTIONS \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: POST" \
    "$BASE_URL/api/v1/agents/zumbi" 2>/dev/null | grep -i "access-control")

if echo "$cors_headers" | grep -q "access-control-allow-origin"; then
    echo -e "${GREEN}✅ CORS configurado${NC}"
else
    echo -e "${RED}❌ CORS não configurado${NC}"
fi

echo ""
echo "=========================================="
echo "RESUMO DO TESTE"
echo "=========================================="

# Testa Portal da Transparência
echo -n "Portal da Transparência: "
response=$(curl -s "$BASE_URL/api/v1/transparency/contracts?year=2024&limit=1")
if echo "$response" | grep -q '"sources":\["FEDERAL-portal"\]'; then
    echo -e "${GREEN}✅ Retornando apenas dados federais${NC}"
elif echo "$response" | grep -q "Access denied"; then
    echo -e "${RED}❌ Ainda bloqueado${NC}"
else
    echo -e "${YELLOW}⚠️  Verificar manualmente${NC}"
fi

echo ""
echo "Teste concluído!"
