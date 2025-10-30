#!/bin/bash
#
# Script para configurar Grafana Cloud no Railway
# Autor: Anderson Henrique da Silva
# Localização: Minas Gerais, Brasil
#

set -e

echo "🔧 Configurando Grafana Cloud no Railway..."
echo ""

# Verificar se railway CLI está instalado
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI não encontrado!"
    echo ""
    echo "Instale com:"
    echo "  npm i -g @railway/cli"
    echo ""
    echo "Ou configure manualmente no Railway Dashboard:"
    echo "  https://railway.app/project/cidadao-ai-backend"
    exit 1
fi

# Verificar se está logado
echo "1️⃣ Verificando login do Railway..."
if ! railway whoami &> /dev/null; then
    echo "❌ Você não está logado no Railway!"
    echo ""
    echo "Execute:"
    echo "  railway login"
    exit 1
fi

echo "   ✅ Logado no Railway"
echo ""

# Configurar variáveis
echo "2️⃣ Configurando variáveis de ambiente..."
echo ""

railway variables set GRAFANA_CLOUD_ENABLED=true
echo "   ✅ GRAFANA_CLOUD_ENABLED=true"

railway variables set GRAFANA_CLOUD_URL="https://prometheus-prod-40-prod-sa-east-1.grafana.net/api/prom/push"
echo "   ✅ GRAFANA_CLOUD_URL configurado"

railway variables set GRAFANA_CLOUD_USER="2768861"
echo "   ✅ GRAFANA_CLOUD_USER=2768861"

railway variables set GRAFANA_CLOUD_KEY="glc_eyJvIjoiMTU3NTU2NiIsIm4iOiJzdGFjay0xNDIyMzEzLWFsbG95LWNpZGFkYW8tYWkiLCJrIjoiYjAybVJrN243aDRHb3hnOXM5NEk3OHlZIiwibSI6eyJyIjoicHJvZC1zYS1lYXN0LTEifX0="
echo "   ✅ GRAFANA_CLOUD_KEY configurado"

# Variáveis opcionais
railway variables set METRICS_PUSH_INTERVAL="60"
echo "   ✅ METRICS_PUSH_INTERVAL=60"

railway variables set METRICS_PUSH_TIMEOUT="10"
echo "   ✅ METRICS_PUSH_TIMEOUT=10"

echo ""
echo "3️⃣ Verificando variáveis configuradas..."
echo ""
railway variables | grep GRAFANA
echo ""

echo "✅ Configuração concluída!"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Deploy no Railway:"
echo "   git push origin main"
echo ""
echo "2. Verificar logs:"
echo "   railway logs --follow"
echo ""
echo "   Procure por:"
echo "   ✅ 'Starting Grafana Cloud metrics push loop (interval: 60s)'"
echo "   ✅ 'Metrics pushed to Grafana Cloud successfully'"
echo ""
echo "3. Importar dashboards no Grafana Cloud:"
echo "   - Login: https://grafana.com/"
echo "   - Dashboards → Import"
echo "   - Upload dos 6 arquivos JSON de monitoring/grafana/dashboards/"
echo ""
echo "4. Verificar métricas (após 1-2 minutos):"
echo "   - Grafana Cloud → Explore"
echo "   - Query: up{job=\"cidadao-ai-backend\"}"
echo ""
echo "📚 Documentação completa:"
echo "   docs/deployment/railway/GRAFANA_CLOUD_SETUP.md"
echo ""
