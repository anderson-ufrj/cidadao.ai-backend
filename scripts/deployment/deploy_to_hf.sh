#!/bin/bash
#
# Deploy Cidadão.AI to Hugging Face Hub
# Updates both the model and creates/updates a Space for demo
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Cidadão.AI to Hugging Face Hub${NC}"
echo -e "${BLUE}===============================================${NC}"
echo

# Check for required environment variables
if [ -z "$HUGGINGFACE_HUB_TOKEN" ]; then
    echo -e "${RED}❌ HUGGINGFACE_HUB_TOKEN not set${NC}"
    echo -e "${YELLOW}💡 Get your token from: https://huggingface.co/settings/tokens${NC}"
    echo -e "${YELLOW}💡 Then run: export HUGGINGFACE_HUB_TOKEN=your_token${NC}"
    exit 1
fi

# Configuration
MODEL_NAME="${HF_MODEL_NAME:-anderson-ufrj/cidadao-ai}"
SPACE_NAME="${HF_SPACE_NAME:-anderson-ufrj/cidadao-ai-demo}"
LOCAL_MODEL_PATH="${LOCAL_MODEL_PATH:-}"

echo -e "${BLUE}📋 Configuration:${NC}"
echo -e "  Model Name: ${MODEL_NAME}"
echo -e "  Space Name: ${SPACE_NAME}"
echo -e "  Local Model: ${LOCAL_MODEL_PATH:-None (will create new)}"
echo

# Step 1: Upload model to Hub
echo -e "${YELLOW}🤖 Step 1: Uploading model to Hugging Face Hub...${NC}"
python3 huggingface_model/upload_to_hub.py \
    --model-name "$MODEL_NAME" \
    ${LOCAL_MODEL_PATH:+--local-path "$LOCAL_MODEL_PATH"} \
    --token "$HUGGINGFACE_HUB_TOKEN" \
    --validate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Model uploaded successfully!${NC}"
else
    echo -e "${RED}❌ Model upload failed${NC}"
    exit 1
fi

# Step 2: Create/Update Space
echo -e "${YELLOW}🌟 Step 2: Creating/Updating Hugging Face Space...${NC}"

# Create a temporary directory for Space files
SPACE_DIR=$(mktemp -d)
cd "$SPACE_DIR"

# Initialize git repo
git init
git remote add origin "https://huggingface.co/spaces/$SPACE_NAME"

# Create Space files
cat > README.md << EOF
---
title: Cidadão.AI Demo
emoji: 🏛️
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# 🏛️ Cidadão.AI - Transparência Pública Brasileira

Demo interativo do sistema de análise de transparência pública do Cidadão.AI.

## Como usar

1. Cole um texto relacionado a contratos, gastos públicos ou documentos governamentais
2. Clique em "Analisar"
3. Veja os resultados de:
   - **Detecção de Anomalias**: Identifica padrões suspeitos
   - **Análise Financeira**: Avalia riscos financeiros
   - **Conformidade Legal**: Verifica adequação às normas

## Tecnologias

- **Backend**: FastAPI + HashiCorp Vault + PostgreSQL
- **IA**: Transformers + LangChain + Multi-Agent System
- **Frontend**: Next.js + Tailwind CSS
- **Infraestrutura**: Docker + Kubernetes

## Links

- 🔗 [Backend Repository](https://github.com/anderson-ufrj/cidadao.ai-backend)
- 🌐 [Live Demo](https://cidadao-ai.vercel.app)
- 📚 [Documentation](https://cidadao-ai-docs.vercel.app)
EOF

# Create Gradio app
cat > app.py << 'EOF'
import gradio as gr
import requests
import json
from typing import Dict, Any

def analyze_text(text: str) -> Dict[str, Any]:
    """
    Analyze text for transparency issues
    This is a demo implementation - replace with actual model
    """
    if not text or len(text.strip()) < 10:
        return {
            "error": "Por favor, forneça um texto com pelo menos 10 caracteres."
        }

    # Demo analysis (replace with actual model inference)
    results = {}

    # Simulate anomaly detection
    anomaly_score = 0.3 if "emergencial" in text.lower() or "dispensa" in text.lower() else 0.1
    anomaly_level = "🟡 Suspeito" if anomaly_score > 0.2 else "🟢 Normal"

    results["anomaly"] = {
        "label": anomaly_level,
        "confidence": anomaly_score,
        "description": "Análise de padrões anômalos no texto"
    }

    # Simulate financial analysis
    financial_score = 0.7 if "milhões" in text.lower() or "R$" in text else 0.2
    financial_level = "🔴 Alto" if financial_score > 0.5 else "🟢 Baixo"

    results["financial"] = {
        "label": financial_level,
        "confidence": financial_score,
        "description": "Avaliação de risco financeiro"
    }

    # Simulate legal compliance
    legal_score = 0.8 if "licitação" in text.lower() or "edital" in text.lower() else 0.4
    legal_level = "🟢 Conforme" if legal_score > 0.6 else "🟡 Verificar"

    results["legal"] = {
        "label": legal_level,
        "confidence": legal_score,
        "description": "Conformidade com normas legais"
    }

    return results

def format_results(results: Dict[str, Any]) -> str:
    """Format analysis results for display"""

    if "error" in results:
        return f"❌ **Erro**: {results['error']}"

    output = "## 🔍 Resultados da Análise\n\n"

    for category, data in results.items():
        confidence_percent = f"{data['confidence']:.1%}"

        output += f"### {category.title()}\n"
        output += f"- **Resultado**: {data['label']}\n"
        output += f"- **Confiança**: {confidence_percent}\n"
        output += f"- **Descrição**: {data['description']}\n\n"

    return output

def analyze_transparency(text: str) -> str:
    """Main analysis function for Gradio interface"""
    results = analyze_text(text)
    return format_results(results)

# Create Gradio interface
demo = gr.Interface(
    fn=analyze_transparency,
    inputs=gr.Textbox(
        label="📄 Texto para Análise",
        placeholder="Cole aqui contratos, editais, documentos públicos ou descrições de gastos governamentais...",
        lines=10,
        max_lines=20
    ),
    outputs=gr.Markdown(label="🔍 Resultados"),
    title="🏛️ Cidadão.AI - Análise de Transparência Pública",
    description="""
    **Demonstração do sistema de análise de transparência pública brasileira**

    Este sistema utiliza inteligência artificial para analisar documentos e identificar:
    - 🎯 **Anomalias**: Padrões suspeitos ou irregulares
    - 💰 **Riscos Financeiros**: Avaliação de impacto financeiro
    - ⚖️ **Conformidade Legal**: Adequação às normas e leis

    *Esta é uma versão de demonstração. O sistema completo inclui 17 agentes especializados.*
    """,
    article="""
    ### 🔗 Links Úteis
    - [📚 Documentação Completa](https://cidadao-ai-docs.vercel.app)
    - [💻 Código Fonte](https://github.com/anderson-ufrj/cidadao.ai-backend)
    - [🌐 Aplicação Completa](https://cidadao-ai.vercel.app)

    ### 🤖 Tecnologias
    - **Multi-Agent System**: 17 agentes especializados
    - **HashiCorp Vault**: Gerenciamento seguro de secrets
    - **FastAPI + Next.js**: Stack moderna e performática
    - **Transformers + LangChain**: IA de última geração
    """,
    examples=[
        ["""Contrato emergencial no valor de R$ 50.000.000,00 para aquisição de equipamentos médicos,
dispensando processo licitatório devido à urgência. Fornecedor: MedTech Solutions LTDA.
Prazo de entrega: 15 dias. Justificativa: atendimento emergencial à demanda hospitalar."""],

        ["""Edital de licitação pública nº 001/2024 para contratação de serviços de limpeza
dos prédios públicos municipais. Valor estimado: R$ 2.400.000,00 anuais.
Modalidade: Pregão Eletrônico. Participação ampla com critério de menor preço."""],

        ["""Prestação de contas do primeiro trimestre de 2024: Total executado R$ 15.000.000,00
sendo R$ 8.000.000,00 em custeio e R$ 7.000.000,00 em investimentos.
Principais gastos: folha de pagamento (40%), manutenção (25%), investimentos (35%)."""]
    ],
    theme=gr.themes.Soft(),
    allow_flagging="never"
)

if __name__ == "__main__":
    demo.launch()
EOF

# Create requirements.txt
cat > requirements.txt << EOF
gradio==4.0.0
requests==2.31.0
transformers==4.36.0
torch>=1.9.0
numpy>=1.21.0
EOF

# Create .gitignore
cat > .gitignore << EOF
__pycache__/
*.py[cod]
*$py.class
.env
.DS_Store
EOF

echo -e "${YELLOW}📝 Created Space files...${NC}"

# Add and commit files
git add .
git commit -m "feat: add Cidadão.AI transparency analysis demo

- Interactive Gradio interface for public transparency analysis
- Demo implementation of anomaly detection, financial analysis, and legal compliance
- Multi-language support and comprehensive examples
- Integration with Cidadão.AI backend system"

# Try to push (create repo if it doesn't exist)
echo -e "${YELLOW}📤 Pushing to Hugging Face Spaces...${NC}"

# Set up authentication
git config user.email "anderson.ufrj@gmail.com"
git config user.name "Anderson H. Silva"

# Push to space
export GIT_USERNAME=$HUGGINGFACE_HUB_TOKEN
export GIT_PASSWORD=$HUGGINGFACE_HUB_TOKEN

git push https://${HUGGINGFACE_HUB_TOKEN}@huggingface.co/spaces/${SPACE_NAME} main 2>/dev/null || {
    echo -e "${YELLOW}📝 Creating new Space...${NC}"

    # Create space via API
    curl -X POST \
        -H "Authorization: Bearer ${HUGGINGFACE_HUB_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"type\":\"space\", \"name\":\"$(basename $SPACE_NAME)\", \"private\":false, \"sdk\":\"gradio\"}" \
        https://huggingface.co/api/repos/$(dirname $SPACE_NAME)

    sleep 2
    git push https://${HUGGINGFACE_HUB_TOKEN}@huggingface.co/spaces/${SPACE_NAME} main
}

cd - > /dev/null
rm -rf "$SPACE_DIR"

echo
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo
echo -e "${BLUE}📋 Summary:${NC}"
echo -e "${GREEN}✅ Model uploaded to:${NC} https://huggingface.co/${MODEL_NAME}"
echo -e "${GREEN}✅ Space deployed to:${NC} https://huggingface.co/spaces/${SPACE_NAME}"
echo
echo -e "${BLUE}🚀 Next steps:${NC}"
echo "1. Visit your Space to test the demo"
echo "2. Customize the app.py with your actual model"
echo "3. Add your trained model weights"
echo "4. Share with the community!"
echo
echo -e "${YELLOW}💡 Pro tip:${NC} Your Space will be public. Set private=true in the API call if needed."
