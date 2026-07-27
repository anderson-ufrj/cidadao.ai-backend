#!/bin/bash
# Script para configurar variáveis de ambiente no Railway
# Após fazer railway login e railway link, execute este script

echo "🚀 Configurando variáveis de ambiente no Railway..."

# LLM Providers
railway variables set MARITACA_API_KEY="$MARITACA_API_KEY"
railway variables set MARITACA_MODEL="sabiazinho-3"
railway variables set LLM_PROVIDER="maritaca"

railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
railway variables set ANTHROPIC_MODEL="claude-sonnet-4-20250514"

# Security Keys (Production)
railway variables set JWT_SECRET_KEY="$JWT_SECRET_KEY"
railway variables set SECRET_KEY="$SECRET_KEY"

# Environment
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="false"

echo "✅ Variáveis configuradas!"
echo ""
echo "📋 Próximos passos:"
echo "  1. Verifique os logs: railway logs"
echo "  2. Abra o projeto: railway open"
echo "  3. Teste a API na URL pública"
