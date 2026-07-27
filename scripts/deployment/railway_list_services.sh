#!/bin/bash

# Railway Service and Variable Discovery
# Helps find the correct service names and variable names for Shared Variables


echo "🔍 Descobrindo serviços e variáveis do Railway..."
echo "=" * 80
echo ""

echo "📋 1. LISTANDO TODOS OS SERVIÇOS DO PROJETO:"
echo "-" * 80
railway service list 2>&1 || echo "❌ Falhou. Tentando alternativa..."
echo ""

echo "📋 2. TENTANDO VER STATUS DO PROJETO:"
echo "-" * 80
railway status 2>&1
echo ""

echo "📋 3. LISTANDO VARIÁVEIS DO POSTGRES:"
echo "-" * 80
echo "Tentando: railway variables --service Postgres"
railway variables --service Postgres 2>&1 || echo "❌ Serviço 'Postgres' não encontrado"
echo ""

echo "Tentando: railway variables --service postgres (minúsculo)"
railway variables --service postgres 2>&1 || echo "❌ Serviço 'postgres' não encontrado"
echo ""

echo "Tentando: railway variables --service PostgreSQL"
railway variables --service PostgreSQL 2>&1 || echo "❌ Serviço 'PostgreSQL' não encontrado"
echo ""

echo "📋 4. LISTANDO VARIÁVEIS DO REDIS:"
echo "-" * 80
echo "Tentando: railway variables --service cidadao-redis"
railway variables --service cidadao-redis 2>&1 || echo "❌ Serviço 'cidadao-redis' não encontrado"
echo ""

echo "Tentando: railway variables --service Redis"
railway variables --service Redis 2>&1 || echo "❌ Serviço 'Redis' não encontrado"
echo ""

echo "📋 5. LISTANDO VARIÁVEIS DO API:"
echo "-" * 80
echo "Tentando: railway variables --service cidadao-api"
railway variables --service cidadao-api 2>&1 || echo "❌ Serviço 'cidadao-api' não encontrado"
echo ""

echo "=" * 80
echo "✅ Descoberta concluída!"
echo ""
echo "🎯 COMO USAR OS RESULTADOS:"
echo "   1. Veja qual nome de serviço FUNCIONOU acima"
echo "   2. Veja o nome EXATO da variável (DATABASE_URL, POSTGRES_URL, etc)"
echo "   3. Use na Shared Variable assim: \${{NOME_SERVICO.NOME_VARIAVEL}}"
echo ""
echo "Exemplo:"
echo "   Se funcionou 'postgres' e a variável é 'DATABASE_URL':"
echo "   DATABASE_URL = \${{postgres.DATABASE_URL}}"
echo ""
