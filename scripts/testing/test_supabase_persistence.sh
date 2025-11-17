#!/bin/bash
# Test Supabase Persistence Script
# Autor: Anderson Henrique da Silva
# Data: 2025-10-09

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_URL="https://cidadao-api-production.up.railway.app"

echo -e "${BLUE}🧪 Teste de Persistência Supabase${NC}"
echo "==========================================="
echo ""

# 1. Testar se API está respondendo
echo -e "${YELLOW}1️⃣  Verificando se API está online...${NC}"
if curl -s --fail "$API_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ API está online!${NC}"
else
    echo -e "${RED}❌ API está offline ou não respondendo${NC}"
    exit 1
fi
echo ""

# 2. Criar uma investigação de teste
echo -e "${YELLOW}2️⃣  Criando investigação de teste...${NC}"
RESPONSE=$(curl -s -X POST "$API_URL/api/v1/investigations" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Teste de persistência Supabase - 2025-10-09",
    "data_source": "contracts",
    "filters": {"test": true, "timestamp": "'$(date +%s)'"}
  }')

echo "Resposta da API:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Extrair ID da investigação
INVESTIGATION_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -z "$INVESTIGATION_ID" ]; then
    echo -e "${RED}❌ Falha ao criar investigação (sem ID retornado)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Investigação criada com ID: $INVESTIGATION_ID${NC}"
echo ""

# 3. Aguardar um pouco para garantir que foi salvo
echo -e "${YELLOW}3️⃣  Aguardando 2 segundos para garantir persistência...${NC}"
sleep 2
echo ""

# 4. Recuperar a investigação
echo -e "${YELLOW}4️⃣  Recuperando investigação do banco...${NC}"
GET_RESPONSE=$(curl -s "$API_URL/api/v1/investigations/$INVESTIGATION_ID")

echo "Dados recuperados:"
echo "$GET_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$GET_RESPONSE"
echo ""

# Verificar se conseguiu recuperar
RECOVERED_ID=$(echo "$GET_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ "$RECOVERED_ID" == "$INVESTIGATION_ID" ]; then
    echo -e "${GREEN}✅ Investigação recuperada com sucesso do Supabase!${NC}"
else
    echo -e "${RED}❌ Falha ao recuperar investigação (pode estar usando in-memory)${NC}"
    exit 1
fi
echo ""

# 5. Listar investigações recentes
echo -e "${YELLOW}5️⃣  Listando investigações recentes...${NC}"
LIST_RESPONSE=$(curl -s "$API_URL/api/v1/investigations?limit=5")

echo "Últimas 5 investigações:"
echo "$LIST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LIST_RESPONSE"
echo ""

# 6. Verificar logs do Railway (via web)
echo "==========================================="
echo -e "${GREEN}✅ Teste de Persistência Concluído!${NC}"
echo ""
echo -e "${BLUE}📊 Próximos Passos de Validação:${NC}"
echo ""
echo "1️⃣  Verificar Supabase Dashboard:"
echo "   🔗 https://supabase.com/dashboard/project/pbsiyuattnwgohvkkkks/editor"
echo "   📋 Tabela: investigations"
echo "   🔍 Procure pelo ID: $INVESTIGATION_ID"
echo ""
echo "2️⃣  Verificar Logs do Railway:"
echo "   🔗 https://railway.app"
echo "   📋 Serviço: cidadao-api"
echo "   🔍 Procure por: 'Using Supabase REST service'"
echo ""
echo "3️⃣  Verificar Auto-Investigations:"
echo "   📋 Celery Beat deve estar criando investigações automáticas"
echo "   🔍 user_id = 'system_auto_monitor'"
echo ""
