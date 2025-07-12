#!/bin/bash

# Deploy via SSH para Hugging Face Spaces
# Uso: ./deploy_hf_ssh.sh [USERNAME]

HF_USERNAME=${1:-"neural-thinker"}
SPACE_NAME="cidadao-ai"
TEMP_DIR=$(mktemp -d)

echo "🚀 Deploy via SSH para Hugging Face Spaces"
echo "👤 Usuário: $HF_USERNAME"
echo "🔐 Usando SSH key configurada"

# Clonar via SSH
echo "📥 Clonando Space via SSH..."
if ! git clone "git@hf.co:spaces/$HF_USERNAME/$SPACE_NAME" "$TEMP_DIR" 2>/dev/null; then
    echo "❌ Space ainda não existe!"
    echo "📝 Por favor, crie o Space primeiro em:"
    echo "   https://huggingface.co/new-space"
    echo ""
    echo "Configurações:"
    echo "- Space name: $SPACE_NAME"
    echo "- SDK: Gradio"
    echo "- License: MIT"
    echo ""
    echo "Depois de criar, rode este script novamente!"
    exit 1
fi

echo "✅ Space clonado com sucesso!"

# Copiar arquivos
echo "📋 Copiando arquivos..."
cp app.py "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"
cp README_HF_SPACES.md "$TEMP_DIR/README.md"

# Entrar no diretório
cd "$TEMP_DIR"

# Configurar git
git config user.name "Anderson H. Silva"
git config user.email "andersonhs27@gmail.com"

# Status
echo "📊 Arquivos modificados:"
git status --short

# Commit e push
echo "📤 Enviando para Hugging Face..."
git add .
git commit -m "Deploy Cidadão.AI - Transparência pública com IA" || echo "Sem mudanças"
git push

# Voltar e limpar
cd -
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Deploy concluído com sucesso!"
echo "🌐 Seu Space: https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"
echo ""
echo "⏳ O Space levará alguns minutos para inicializar..."
echo "🔄 Você pode acompanhar o progresso na página do Space"
echo ""
echo "🎉 Parabéns! O Cidadão.AI está no ar!"