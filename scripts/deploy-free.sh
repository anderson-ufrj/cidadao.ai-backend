#!/bin/bash

# Deploy Gratuito do Cidadão.AI
# Usando Vercel (frontend) + Railway (backend) + Supabase (database)

echo "🚀 Iniciando deploy gratuito do Cidadão.AI..."

# Frontend no Vercel
echo "📦 Deploy do Frontend no Vercel..."
cd frontend
npx vercel --prod
cd ..

# Backend no Railway
echo "🚂 Deploy do Backend no Railway..."
railway login
railway init
railway add
railway up

# Alternativa: Backend no Render
# echo "🎨 Deploy do Backend no Render..."
# render create --name cidadao-api --file render.yaml

echo "✅ Deploy concluído!"
echo "📝 Próximos passos:"
echo "1. Configure as variáveis de ambiente no Railway/Render"
echo "2. Atualize o CORS no backend para o domínio do Vercel"
echo "3. Configure o Supabase para o banco de dados"

echo "🔗 URLs:"
echo "Frontend: https://cidadao-ai.vercel.app"
echo "Backend: https://cidadao-api.railway.app"