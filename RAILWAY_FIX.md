# 🚨 CORREÇÃO URGENTE - Investigações Travadas

## Problema
As investigações estão travando em 30% porque o LLM (Groq) não está respondendo.

## Solução Rápida (5 minutos)

### 1️⃣ Verificar/Adicionar GROQ_API_KEY no Railway

1. Acesse o Railway Dashboard
2. Vá para o serviço `cidadao-api-production`
3. Clique em **Variables** (ou Settings → Variables)
4. Verifique se existe `GROQ_API_KEY`

Se não existir ou estiver expirada:
- Obtenha uma nova chave em: https://console.groq.com/keys
- Adicione: `GROQ_API_KEY = gsk_xxxxxxxxxxxxx`

### 2️⃣ Adicionar MARITACA_API_KEY como Backup (Opcional)

Para ter um fallback em português:
1. Obtenha chave em: https://chat.maritaca.ai
2. Adicione no Railway: `MARITACA_API_KEY = sk-xxxxxxxxxxxxx`

### 3️⃣ Reiniciar o Serviço

Após adicionar as variáveis:
1. No Railway, clique em **Deployments**
2. Clique no deploy atual
3. Selecione **Restart** ou faça um novo deploy

## Teste Rápido

```bash
# Teste simples via curl
curl -X POST https://cidadao-api-production.up.railway.app/api/v1/investigations/start \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Teste após correção",
    "data_source": "contracts",
    "filters": {},
    "anomaly_types": ["price"]
  }'

# Aguarde 10 segundos e verifique o status (substitua o ID retornado)
curl https://cidadao-api-production.up.railway.app/api/v1/investigations/{ID}/status
```

## Verificação nos Logs

No Railway, vá em **Logs** e procure por:
- `groq_client_initialized` - Deve aparecer se a chave está configurada
- `LLM request success` - Indica que o LLM está respondendo
- `investigation_completed` - Investigação concluída com sucesso

## Correção Permanente (Próximos Commits)

Para evitar travamentos futuros, vamos adicionar:

1. **Timeout menor** (30s ao invés de 60s)
2. **Fallback para análise sem LLM** quando houver timeout
3. **Mock response** para desenvolvimento/testes

## Status Esperado Após Correção

- ✅ Investigações completam em 15-30 segundos
- ✅ Progresso vai de 0% → 30% → 70% → 100%
- ✅ Resultados são salvos no PostgreSQL
- ✅ Anomalias são detectadas e reportadas

## Contato

Se o problema persistir após adicionar a GROQ_API_KEY:
1. Verifique os rate limits (14,400 tokens/min)
2. Tente com MARITACA_API_KEY
3. Verifique os logs completos no Railway
