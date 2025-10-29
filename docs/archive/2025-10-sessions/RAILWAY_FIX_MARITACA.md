# 🚨 CORREÇÃO URGENTE - Investigações Travadas com Maritaca AI

## Problema Identificado
As investigações estão travando em 30% porque:
1. O sistema está configurado para usar **Groq** por padrão (`llm_provider: "groq"`)
2. Vocês querem usar **Maritaca AI** (modelo brasileiro)
3. A configuração não está apontando para Maritaca

## Solução Imediata no Railway (5 minutos)

### 1️⃣ Configurar Maritaca no Railway

Acesse o Railway Dashboard → Serviço `cidadao-api-production` → **Variables** e adicione/verifique:

```env
# Configurar Maritaca como provider principal
LLM_PROVIDER=maritaca

# API Key da Maritaca (obter em https://chat.maritaca.ai)
MARITACA_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx

# Modelo da Maritaca (use sabiazinho-3 que é mais barato)
LLM_MODEL_NAME=sabiazinho-3
```

### 2️⃣ Remover/Comentar GROQ se existir

Se houver `GROQ_API_KEY` configurada, você pode:
- Removê-la completamente
- Ou mantê-la como backup

### 3️⃣ Variáveis Completas Recomendadas

```env
# LLM Principal - Maritaca AI
LLM_PROVIDER=maritaca
MARITACA_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
LLM_MODEL_NAME=sabiazinho-3
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048

# Banco de Dados (já deve estar configurado)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Segurança (já devem estar configurados)
JWT_SECRET_KEY=xxxxx
SECRET_KEY=xxxxx
```

### 4️⃣ Reiniciar o Serviço

Após adicionar as variáveis:
1. No Railway, clique em **Deployments**
2. O serviço reiniciará automaticamente ao detectar mudanças nas variáveis
3. Aguarde 1-2 minutos para o novo deploy

## Como Obter a API Key da Maritaca

1. Acesse: https://chat.maritaca.ai
2. Faça login ou crie uma conta
3. Vá em **Configurações** → **API Keys**
4. Crie uma nova chave
5. Copie e adicione no Railway como `MARITACA_API_KEY`

## Teste Rápido Após Configuração

```bash
# Criar investigação
curl -X POST https://cidadao-api-production.up.railway.app/api/v1/investigations/start \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Teste com Maritaca AI",
    "data_source": "contracts",
    "filters": {"ano": 2024},
    "anomaly_types": ["price"]
  }'

# Resposta esperada:
# {"investigation_id": "xxx", "status": "started", "message": "Investigation queued"}

# Aguarde 15-30 segundos e verifique o status
curl https://cidadao-api-production.up.railway.app/api/v1/investigations/{ID}/status
```

## Verificação nos Logs do Railway

Após reiniciar, procure nos logs por:

✅ **Sucesso**:
```
maritaca_client_initialized
LLM provider: maritaca
Investigation completed successfully
Progress: 100%
```

❌ **Problemas**:
```
MARITACA_API_KEY not found
Failed to initialize Maritaca
LLM timeout
```

## Modelos Disponíveis da Maritaca

- `sabiazinho-3` - Mais barato e eficiente ✅ (Recomendado)
- `sabia-3` - Modelo padrão
- `sabia-3-medium` - Mais capacidade
- `sabia-3-large` - Máxima capacidade

## Ajuste Fino para Maritaca

Se quiser otimizar ainda mais, adicione:

```env
# Configurações específicas para Maritaca
LLM_TEMPERATURE=0.5  # Mais determinístico para análises
LLM_MAX_TOKENS=3000  # Maritaca suporta até 8192
LLM_TOP_P=0.95       # Melhor para português
```

## Fallback Manual (Temporário)

Se ainda não tiver a API key da Maritaca, você pode temporariamente usar um mock:

```env
LLM_PROVIDER=mock
# Isso fará o sistema usar respostas simuladas (não recomendado para produção)
```

## Correção no Código (Próximo Deploy)

Para garantir que Maritaca seja usado corretamente, precisamos:

1. Adicionar Maritaca como provider oficial no `llm/providers.py`
2. Configurar fallback automático
3. Adicionar retry com backoff específico para Maritaca

## Status Esperado Após Correção

- ✅ Investigações completam em 20-40 segundos
- ✅ Progresso: 0% → 30% → 70% → 100%
- ✅ Mensagens em português nativo
- ✅ Melhor compreensão de termos brasileiros
- ✅ Dados salvos no PostgreSQL

## Troubleshooting

### Se continuar travando em 30%:
1. Verifique se `LLM_PROVIDER=maritaca` está configurado
2. Confirme que a API key é válida
3. Teste a API key localmente:

```python
import httpx

headers = {
    "Authorization": f"Bearer {SUA_API_KEY}",
    "Content-Type": "application/json"
}

response = httpx.post(
    "https://chat.maritaca.ai/api/chat/completions",
    headers=headers,
    json={
        "model": "sabiazinho-3",
        "messages": [{"role": "user", "content": "Olá"}]
    }
)
print(response.status_code)  # Deve ser 200
```

### Rate Limits da Maritaca:
- Verifique os limites da sua conta
- Use `sabiazinho-3` que é mais econômico
- Implemente cache para queries repetidas

## Contato e Suporte

- Maritaca AI: https://chat.maritaca.ai/docs
- Railway: Verifique os logs em tempo real
- Alternativa: Configure GROQ_API_KEY como fallback
