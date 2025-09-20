# 🚨 Correção Urgente - Backend HuggingFace

## Problema Identificado

O backend no HuggingFace está rodando a versão **ERRADA** do código:

1. **Versão atual** (app.py): Apenas tem o EnhancedZumbiAgent
2. **Versão correta** (src/api/app.py): Sistema completo com Drummond e todos os agentes

Por isso o frontend sempre retorna "modo manutenção" - o Drummond não existe!

## Solução Imediata

### Opção 1: Substituir app.py (Mais Simples)

```bash
# No branch hf-fastapi
git checkout hf-fastapi

# Backup do app.py atual
mv app.py app_simple.py

# Criar novo app.py que importa o sistema completo
cat > app.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.app import app
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port, forwarded_allow_ips="*", proxy_headers=True)
EOF

# Commit e push
git add app.py app_simple.py
git commit -m "fix: use full multi-agent system with Drummond in HuggingFace deployment"
git push origin hf-fastapi
```

### Opção 2: Adicionar Drummond ao app.py Atual

Se preferir manter o app.py simplificado, adicione o Drummond:

```python
# No app.py, após a linha 522 (onde cria enhanced_zumbi):
from src.agents.drummond_simple import SimpleDrummondAgent
drummond_agent = SimpleDrummondAgent()

# Adicionar endpoint do Drummond
@app.post("/api/v1/chat/message")
async def chat_message(request: ChatRequest):
    """Chat endpoint with Drummond agent."""
    try:
        response = await drummond_agent.process_message(request.message)
        return {
            "status": "success",
            "agent": "drummond",
            "message": response,
            "is_demo_mode": False
        }
    except Exception as e:
        logger.error(f"Drummond error: {str(e)}")
        return {
            "status": "maintenance",
            "agent": "system",
            "message": "Sistema em manutenção temporária",
            "is_demo_mode": True
        }
```

## Correção do Erro 403 da API

O erro 403 indica que a API key do Portal da Transparência está inválida:

1. Verifique no HuggingFace Spaces Settings:
   - Vá para: https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend/settings
   - Procure por `TRANSPARENCY_API_KEY`
   - Se não existir ou estiver inválida, adicione uma nova

2. Para obter nova API key:
   - Acesse: https://www.portaldatransparencia.gov.br/api-de-dados
   - Cadastre-se e gere uma nova chave
   - Adicione no HuggingFace Spaces

## Deploy Correto

```bash
# Após fazer as correções
git push origin hf-fastapi

# O HuggingFace deve fazer redeploy automático
# Se não, vá em Settings > Factory reboot
```

## Verificação

Após o deploy, teste:

```bash
# Verificar se Drummond está disponível
curl https://neural-thinker-cidadao-ai-backend.hf.space/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, como você pode me ajudar?"}'

# Deve retornar resposta do Drummond, não "modo manutenção"
```

## Resumo

1. **Problema**: Versão errada deployada (sem Drummond)
2. **Solução**: Usar app.py que importa src.api.app completo
3. **Extra**: Corrigir API key do Portal da Transparência
4. **Resultado**: Frontend funcionará normalmente com chat ativo