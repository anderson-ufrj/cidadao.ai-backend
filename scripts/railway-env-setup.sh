#!/bin/bash
# Script para configurar variáveis de ambiente no Railway
# Após fazer railway login e railway link, execute este script

echo "🚀 Configurando variáveis de ambiente no Railway..."

# LLM Providers
railway variables set MARITACA_API_KEY="114276428450504196312_22f92d14b8c6e836"
railway variables set MARITACA_MODEL="sabiazinho-3"
railway variables set LLM_PROVIDER="maritaca"

railway variables set ANTHROPIC_API_KEY="***REDACTED-ANTHROPIC-KEY***"
railway variables set ANTHROPIC_MODEL="claude-sonnet-4-20250514"

# Security Keys (Production)
railway variables set JWT_SECRET_KEY="TOE5pPSfQRNqoQigSZmXS6xwYV4-giADkDClR-584jCUocothaIEsJbAW5vT7F8YbIXP0fcxOSVBtD_GWRT9Pg"
railway variables set SECRET_KEY="CPE3OM2D2Qn2ie4-lI4fqmMCm_-pCIDPduLnfe7mX-4mZowcgaaJ7YDiwF5dHH0HrKYD2YSvqRnCZXj-NRwRIQ"

# Environment
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="false"

echo "✅ Variáveis configuradas!"
echo ""
echo "📋 Próximos passos:"
echo "  1. Verifique os logs: railway logs"
echo "  2. Abra o projeto: railway open"
echo "  3. Teste a API na URL pública"
