#!/bin/bash

# Script para deploy automático no Hugging Face Spaces
# Uso: ./deploy_to_hf.sh SEU_USERNAME

HF_USERNAME=${1:-"neural-thinker"}
SPACE_NAME="cidadao-ai"

echo "🚀 Iniciando deploy para Hugging Face Spaces..."
echo "👤 Usuário: $HF_USERNAME"
echo "📦 Space: $SPACE_NAME"

# Verificar se o usuário tem o HF CLI instalado
if ! command -v huggingface-cli &> /dev/null; then
    echo "❌ Hugging Face CLI não encontrado. Instalando..."
    pip install huggingface-hub
fi

# Login no HF (se necessário)
echo "🔐 Fazendo login no Hugging Face..."
echo "Se solicitado, cole seu token de: https://huggingface.co/settings/tokens"
huggingface-cli login

# Criar diretório temporário
TEMP_DIR=$(mktemp -d)
echo "📁 Diretório temporário: $TEMP_DIR"

# Clonar ou criar o Space
echo "📥 Clonando Space..."
if ! git clone "https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME" "$TEMP_DIR" 2>/dev/null; then
    echo "📝 Space não existe. Criando novo..."
    huggingface-cli repo create "$SPACE_NAME" --type space --space_sdk gradio
    git clone "https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME" "$TEMP_DIR"
fi

# Copiar arquivos necessários
echo "📋 Copiando arquivos..."
cp app.py "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"
cp README_HF_SPACES.md "$TEMP_DIR/README.md"

# Se quiser incluir o código fonte completo (opcional)
# mkdir -p "$TEMP_DIR/src"
# cp -r src/* "$TEMP_DIR/src/" 2>/dev/null || true

# Entrar no diretório e fazer commit
cd "$TEMP_DIR"

# Configurar git
git config user.name "Cidadão.AI Deployer"
git config user.email "deploy@cidadao.ai"

# Adicionar, commitar e push
echo "📤 Enviando para Hugging Face..."
git add .
git commit -m "Deploy Cidadão.AI - $(date '+%Y-%m-%d %H:%M:%S')" || echo "Sem mudanças para commitar"
git push

# Limpar
cd -
rm -rf "$TEMP_DIR"

echo "✅ Deploy concluído!"
echo "🌐 Acesse seu Space em: https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"
echo ""
echo "⏳ Aguarde alguns minutos para o Space inicializar..."
echo "💡 Dica: Você pode acompanhar o build em tempo real no site!"