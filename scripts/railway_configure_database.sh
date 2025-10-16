#!/bin/bash

# Railway Database Configuration Script
# Configura DATABASE_URL e REDIS_URL no cidadao-api usando Railway CLI
#
# USO: ./scripts/railway_configure_database.sh

export RAILWAY_TOKEN=9c8d2a3d-bf20-454e-8fe1-8296c5e57fa7

echo "🚀 Configurando DATABASE_URL e REDIS_URL no cidadao-api..."
echo "=" * 80
echo ""

# URLs dos serviços (Railway internal network - mais rápido)
DATABASE_URL="postgresql://postgres:***REDACTED-PG-PASSWORD***@postgres.railway.internal:5432/railway"
REDIS_URL="redis://default:***REDACTED-REDIS-PASSWORD***@cidadao-redis.railway.internal:6379"

echo "📋 1. Configurando DATABASE_URL no cidadao-api..."
railway variables --service cidadao-api --set "DATABASE_URL=$DATABASE_URL"
echo "✅ DATABASE_URL configurado!"
echo ""

echo "📋 2. Configurando REDIS_URL no cidadao-api..."
railway variables --service cidadao-api --set "REDIS_URL=$REDIS_URL"
echo "✅ REDIS_URL configurado!"
echo ""

echo "📋 3. Configurando DATABASE_URL no cidadao.ai-worker..."
railway variables --service cidadao.ai-worker --set "DATABASE_URL=$DATABASE_URL" 2>&1 || echo "⚠️  Worker não encontrado (ok se não existir ainda)"
echo ""

echo "📋 4. Configurando REDIS_URL no cidadao.ai-worker..."
railway variables --service cidadao.ai-worker --set "REDIS_URL=$REDIS_URL" 2>&1 || echo "⚠️  Worker não encontrado (ok se não existir ainda)"
echo ""

echo "📋 5. Configurando DATABASE_URL no cidadao.ai-beat..."
railway variables --service cidadao.ai-beat --set "DATABASE_URL=$DATABASE_URL" 2>&1 || echo "⚠️  Beat não encontrado (ok se não existir ainda)"
echo ""

echo "📋 6. Configurando REDIS_URL no cidadao.ai-beat..."
railway variables --service cidadao.ai-beat --set "REDIS_URL=$REDIS_URL" 2>&1 || echo "⚠️  Beat não encontrado (ok se não existir ainda)"
echo ""

echo "=" * 80
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo ""
echo "🔍 Verificando variáveis do cidadao-api..."
railway variables --service cidadao-api | grep -E "(DATABASE_URL|REDIS_URL)"
echo ""
echo "🚀 PRÓXIMO PASSO:"
echo "   1. Acesse Railway Dashboard"
echo "   2. Clique em 'cidadao-api'"
echo "   3. Clique em 'Redeploy' (botão superior direito)"
echo "   4. Aguarde 2 minutos"
echo "   5. Veja os logs - deve aparecer: 🐘 Using PostgreSQL direct connection"
echo ""
