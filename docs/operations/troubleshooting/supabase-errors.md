# 🔧 HuggingFace Spaces + Supabase REST API Fix

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## 📋 Problema Identificado (2025-10-07 20:19)

Ao analisar os logs do HuggingFace Spaces, identificamos que:

1. ✅ **Código enviado** - Serviços REST API criados
2. ✅ **Variáveis configuradas** - `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` adicionadas aos secrets
3. ❌ **Dependências NÃO instaladas** - O rebuild não instalou os pacotes Supabase

### 🔍 Evidência nos Logs

**O que NÃO estava aparecendo:**
```json
{"event": "Supabase REST service initialized successfully"}
```

**O que continuava aparecendo:**
```json
{"error": "[Errno 101] Network is unreachable", "event": "database_pool_creation_failed"}
{"event": "Running without database connection - some features may be limited"}
```

Isso indicava que o código ainda estava tentando usar **conexão PostgreSQL direta** (asyncpg), em vez da **REST API**.

## ✅ Solução Aplicada

### 1. Atualização do requirements.txt

Adicionamos dependências Supabase de forma **explícita** e com **versões fixas**:

```txt
# Supabase client for REST API access (CRITICAL for HuggingFace Spaces)
supabase>=2.3.0
gotrue>=2.4.0
postgrest>=0.16.0
storage3>=0.7.0
realtime>=2.0.0
supafunc>=0.3.0
```

### 2. Criado Investigation Service Selector Inteligente

**Arquivo**: `src/services/investigation_service_selector.py`

Este módulo **detecta automaticamente** o ambiente e escolhe o serviço correto:

```python
# HuggingFace Spaces → REST API
# Local com PostgreSQL → Conexão direta
# Fallback → In-memory
```

**Funcionalidades**:
- ✅ Detecta variável `SPACE_ID` (HuggingFace Spaces)
- ✅ Verifica configuração `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`
- ✅ Seleciona REST API automaticamente para HuggingFace
- ✅ Usa conexão direta se PostgreSQL disponível localmente

### 3. Código Atualizado Para Usar Serviço Inteligente

**Arquivos modificados**:
- `src/api/graphql/schema.py` → Usa REST API automático
- `src/api/routes/export.py` → Usa REST API automático
- `src/services/cache_warming_service.py` → Usa REST API automático
- `src/infrastructure/queue/tasks/investigation_tasks.py` → Usa REST API automático

**Antes**:
```python
from src.services.investigation_service import investigation_service  # ❌ PostgreSQL direto
```

**Depois**:
```python
from src.services.investigation_service_selector import investigation_service  # ✅ Auto-seleciona
```

### 4. Commit e Push

```bash
git add .
git commit -m "fix(supabase): auto-detect environment and use REST API on HuggingFace

- Created investigation_service_selector.py for smart service selection
- Detects HuggingFace Spaces via SPACE_ID environment variable
- Automatically uses REST API when on HuggingFace
- Falls back to PostgreSQL direct connection when available
- Updated all service imports to use selector"

git push origin main
git push huggingface main
```

## 📊 Como Monitorar o Fix

### 1. Aguardar Rebuild (2-5 minutos)

Acesse: https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend/logs

### 2. Verificar Instalação das Dependências

Nos logs de BUILD, você deve ver:

```
Collecting supabase>=2.3.0
  Downloading supabase-2.x.x-py3-none-any.whl
Collecting gotrue>=2.4.0
  Downloading gotrue-2.x.x-py3-none-any.whl
Collecting postgrest>=0.16.0
  Downloading postgrest-0.x.x-py3-none-any.whl
...
Successfully installed supabase-2.x.x gotrue-2.x.x postgrest-0.x.x
```

### 3. Verificar Inicialização Bem-Sucedida

Nos logs de APPLICATION, você deve ver:

```json
{"event": "Initializing Supabase REST client", "logger": "src.services.supabase_service_rest"}
{"event": "Supabase REST service initialized successfully", "logger": "src.services.supabase_service_rest"}
```

### 4. Testar Criação de Investigação

```bash
curl -X POST https://neural-thinker-cidadao-ai-backend.hf.space/api/v1/investigations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "302573ff-3416-43a3-a074-24bd7c6ed50a",
    "query": "Test via REST API",
    "data_source": "contracts"
  }'
```

Deve retornar:
```json
{
  "id": "uuid-aqui",
  "status": "pending",
  "query": "Test via REST API",
  ...
}
```

## ✅ Checklist de Validação

Use esta lista para confirmar que tudo está funcionando:

- [x] **Código atualizado** - Seletor automático criado
- [x] **Imports modificados** - Todas rotas usando novo serviço
- [ ] **Rebuild iniciado** - HuggingFace mostra "Building..."
- [ ] **Dependências instaladas** - Logs mostram `Successfully installed supabase-2.x.x`
- [ ] **Serviço inicializado** - Logs mostram `Supabase REST service initialized successfully`
- [ ] **Sem erros de rede** - NÃO aparecem `[Errno 101] Network is unreachable`
- [ ] **API responde** - Endpoint `/health` retorna 200
- [ ] **Investigação cria** - POST `/api/v1/investigations` funciona
- [ ] **Dados persistem** - Consulta no Supabase Dashboard mostra registros

## 🔥 Se Ainda Não Funcionar

### Opção 1: Rebuild Manual Forçado

1. Acesse: https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend/settings
2. Clique em **"Factory reboot"** ou **"Rebuild this space"**
3. Aguarde rebuild completo

### Opção 2: Verificar Cache de Dependências

HuggingFace pode estar usando cache antigo:

```bash
# Adicionar este arquivo para forçar limpeza de cache
echo "# Force rebuild $(date)" >> .rebuild-trigger
git add .rebuild-trigger
git commit -m "chore: force clean rebuild"
git push huggingface main
```

### Opção 3: Usar Dockerfile Personalizado

Se requirements.txt não funcionar, criar `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências explicitamente
RUN pip install --no-cache-dir \
    supabase==2.3.0 \
    gotrue==2.4.0 \
    postgrest==0.16.0 \
    storage3==0.7.0 \
    realtime==2.0.0 \
    supafunc==0.3.0

# Copiar e instalar resto das dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

## 📝 Próximos Passos

Após confirmar que o Supabase REST API está funcionando:

1. ✅ **Código atualizado** - Seletor automático implementado
2. ✅ **Imports modificados** - Todas rotas usando serviço inteligente
3. **Testar fluxo completo** de investigação no HuggingFace
4. **Verificar persistência** no Supabase Dashboard
5. **Monitorar performance** (REST API tem ~20-30ms de latência vs ~5-10ms conexão direta)
6. **Documentar logs de sucesso** para referência futura

## 🎯 Resultado Esperado

Após o fix estar completo, quando um agente criar uma investigação:

**No HuggingFace Spaces:**
```json
{"event": "investigation_created", "investigation_id": "uuid", "user_id": "..."}
{"event": "Supabase REST API request successful", "endpoint": "investigations"}
```

**No Supabase Dashboard:**
```sql
SELECT * FROM investigations ORDER BY created_at DESC LIMIT 1;
-- Deve mostrar a investigação recém-criada
```

**No Frontend:**
- Dados aparecem em tempo real
- Progresso atualiza automaticamente
- Sem erros de "Network unreachable"

---

**Status**: 🟢 **CÓDIGO PRONTO - AGUARDANDO DEPLOY** (atualizado em 2025-10-07 20:45)

**Próxima ação**: Commit e push para HuggingFace, então monitorar logs

**Autor**: Anderson H. Silva
**Data**: 2025-10-07
**Última atualização**: 2025-10-07 20:45 (Solução completa com seletor automático)
