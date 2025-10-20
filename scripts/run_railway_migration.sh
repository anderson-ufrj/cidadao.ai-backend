#!/bin/bash

echo "🚀 Rodando migration no Railway..."
echo ""

# O DATABASE_URL do Railway já está configurado nas variáveis de ambiente
# Vamos usar alembic para rodar a migration

echo "📊 Verificando migrations pendentes..."
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/alembic current

echo ""
echo "⬆️  Aplicando migrations..."
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/alembic upgrade head

echo ""
echo "✅ Migration concluída!"
