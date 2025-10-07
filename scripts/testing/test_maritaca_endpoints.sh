#!/bin/bash
# Script para testar os endpoints de chat com Maritaca AI

BASE_URL="https://neural-thinker-cidadao-ai-backend.hf.space"

echo "=== Testando Endpoints de Chat com Maritaca AI ==="
echo ""

# 1. Teste do endpoint /api/v1/chat/stable
echo "1. Testando /api/v1/chat/stable (recomendado):"
curl -X POST "$BASE_URL/api/v1/chat/stable" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá, como você pode me ajudar com transparência pública?",
    "session_id": "test-stable-123"
  }' | jq .

echo ""
echo "----------------------------------------"
echo ""

# 2. Teste do endpoint /api/v1/chat/simple/maritaca
echo "2. Testando /api/v1/chat/simple/maritaca:"
curl -X POST "$BASE_URL/api/v1/chat/simple/maritaca" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quero investigar contratos da saúde",
    "session_id": "test-simple-456"
  }' | jq .

echo ""
echo "----------------------------------------"
echo ""

# 3. Teste do endpoint /api/v1/chat/optimized
echo "3. Testando /api/v1/chat/optimized (com Drummond):"
curl -X POST "$BASE_URL/api/v1/chat/optimized" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Me explique o que é o Cidadão.AI",
    "session_id": "test-optimized-789",
    "use_drummond": true
  }' | jq .

echo ""
echo "----------------------------------------"
echo ""

# 4. Teste do endpoint /api/v1/chat/emergency
echo "4. Testando /api/v1/chat/emergency (ultra resiliente):"
curl -X POST "$BASE_URL/api/v1/chat/emergency" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Como posso analisar gastos públicos?",
    "session_id": "test-emergency-999"
  }' | jq .

echo ""
echo "=== Fim dos Testes ==="