# 🔗 Railway + Supabase - Configuração Completa

**Autor**: Anderson Henrique da Silva
**Data**: 2025-10-09 09:35:00 -03:00 (Minas Gerais, Brasil)
**Propósito**: Habilitar persistência de investigações no Supabase via Railway

---

## 🎯 Objetivo

Resolver o problema: **Investigações automáticas não estão sendo salvas no Supabase desde a migração para Railway (07/10/2025)**.

---

## 🔍 Diagnóstico do Problema

### ❌ Situação Atual (Railway)

```python
# investigation_service_selector.py verifica:
SUPABASE_URL = os.getenv("SUPABASE_URL")  # ❌ None
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # ❌ None

# Resultado: Falls back to in-memory service
# Consequência: Dados perdidos quando container reinicia
```

### ✅ Solução

Adicionar 3 variáveis de ambiente no Railway para que o código use `InvestigationServiceSupabaseRest`.

---

## 📋 Passo a Passo: Adicionar Variáveis no Railway

### 1. Acessar Railway

```
🌐 URL: https://railway.app
👤 Login: anderson-ufrj@hotmail.com (ou sua conta)
```

### 2. Navegar até o Projeto

```
Dashboard → Projetos → cidadao.ai-backend
```

### 3. Adicionar Variáveis

Você precisa adicionar as variáveis em **TODOS os 3 serviços**:
- 🔹 **cidadao-api** (API FastAPI)
- 🔹 **cidadao-worker** (Celery Worker)
- 🔹 **cidadao-beat** (Celery Beat Scheduler)

#### Para cada serviço:

1. **Clique no serviço** (ex: cidadao-api)
2. **Vá na aba**: Variables
3. **Clique em**: New Variable (ou Add Variable)
4. **Adicione estas 3 variáveis**:

```bash
# Variável 1
SUPABASE_URL=https://pbsiyuattnwgohvkkkks.supabase.co

# Variável 2
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBic2l5dWF0dG53Z29odmtra2tzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzU1NTg3MCwiZXhwIjoyMDUzMTMxODcwfQ.aCtc21nAF5aw23FiP9z-fmUQMfjptW93gXD9oZfqRoE

# Variável 3 (opcional mas recomendado)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBic2l5dWF0dG53Z29odmtra2tzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc1NTU4NzAsImV4cCI6MjA1MzEzMTg3MH0.lCIslpyNJZ0bv3dDuZ9AKM-SHw2mYiITNc4lzPJlY04
```

5. **Salvar**: Railway vai automaticamente redesplegar

### 4. Aguardar Redesploy

```
⏱️ Tempo estimado: 2-3 minutos por serviço
🔄 Status: Acompanhe em "Deployments"
✅ Pronto quando: Status = "Active" (verde)
```

---

## 🧪 Verificação: Como Saber se Funcionou

### Método 1: Verificar Logs do Railway

1. **Acesse o serviço** cidadao-api
2. **Clique em**: Deployments → Latest → View Logs
3. **Procure por**:

```log
# ✅ Sucesso (deve aparecer):
INFO: Using Supabase REST service for investigations
INFO: Supabase connection established: https://pbsiyuattnwgohvkkkks.supabase.co

# ❌ Erro (não deve aparecer):
WARNING: SUPABASE_URL not configured, using in-memory storage
```

### Método 2: Testar API de Investigação

```bash
# Criar uma investigação de teste
curl -X POST "https://cidadao-api-production.up.railway.app/api/v1/investigations" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Teste de persistência Railway+Supabase",
    "data_source": "contracts",
    "filters": {"test": true}
  }'

# Resposta esperada:
{
  "id": "uuid-da-investigacao",
  "status": "pending",
  "query": "Teste de persistência Railway+Supabase",
  ...
}
```

### Método 3: Verificar Supabase Diretamente

1. **Acesse**: https://supabase.com/dashboard/project/pbsiyuattnwgohvkkkks
2. **Vá em**: Table Editor → investigations
3. **Verifique**: Deve ter novas linhas com timestamp recente

---

## 🔄 Como o Sistema Funciona Após Configuração

### Fluxo de Dados

```
┌─────────────────────────┐
│  Celery Beat Scheduler  │
│  (a cada 30 minutos)    │
└───────────┬─────────────┘
            │ Trigger
            ↓
┌─────────────────────────────────┐
│  Auto Investigation Task        │
│  (verifica contratos suspeitos) │
└───────────┬─────────────────────┘
            │ Cria investigação
            ↓
┌──────────────────────────────────────────────┐
│  investigation_service_selector              │
│  ✅ Detecta SUPABASE_URL configurado         │
│  ✅ Retorna InvestigationServiceSupabaseRest │
└───────────┬──────────────────────────────────┘
            │ REST API call
            ↓
┌────────────────────────────────┐
│  Supabase PostgreSQL Database  │
│  📊 Tabela: investigations     │
│  ✅ Dados salvos permanentemente│
└────────────────────────────────┘
```

### Endpoints Supabase Usados

O código usa estes endpoints do Supabase REST API:

```python
# CREATE
POST https://pbsiyuattnwgohvkkkks.supabase.co/rest/v1/investigations
Headers:
  apikey: {SUPABASE_SERVICE_ROLE_KEY}
  Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}

# READ
GET https://pbsiyuattnwgohvkkkks.supabase.co/rest/v1/investigations?id=eq.{id}

# UPDATE
PATCH https://pbsiyuattnwgohvkkkks.supabase.co/rest/v1/investigations?id=eq.{id}

# DELETE
DELETE https://pbsiyuattnwgohvkkkks.supabase.co/rest/v1/investigations?id=eq.{id}
```

---

## 🔒 Segurança: Por que SERVICE_ROLE_KEY?

### Tipos de Keys do Supabase

| Key | Uso | Permissões | Expõe ao Frontend? |
|-----|-----|------------|--------------------|
| **anon** | Cliente público | RLS aplicado | ✅ Sim |
| **service_role** | Backend privado | **Bypass RLS** | ❌ NUNCA |

### No Nosso Caso

Usamos `SERVICE_ROLE_KEY` porque:
1. ✅ **Backend server-side**: Railway API/Worker são privados
2. ✅ **Bypass RLS necessário**: Sistema cria investigações automáticas sem user_id real
3. ✅ **Não exposto**: Key fica apenas em variáveis de ambiente do Railway
4. ✅ **Row Level Security**: Ainda protege quando usuários consultam via API

### RLS Policies Aplicadas

```sql
-- Usuários só veem suas próprias investigações
CREATE POLICY "Users can view own investigations"
ON investigations FOR SELECT
USING (auth.uid()::text = user_id OR user_id = 'system_auto_monitor');

-- Sistema pode criar para qualquer user_id
CREATE POLICY "Service can insert investigations"
ON investigations FOR INSERT
WITH CHECK (true);
```

---

## 📊 Monitoramento

### Métricas Importantes

Após configuração, monitore:

1. **Criação de investigações**:
   - Query: `SELECT COUNT(*) FROM investigations WHERE created_at > NOW() - INTERVAL '1 hour'`
   - Esperado: ~2-5 por hora (auto-investigations)

2. **Investigações automáticas**:
   - Query: `SELECT COUNT(*) FROM investigations WHERE user_id = 'system_auto_monitor'`
   - Esperado: Crescendo continuamente

3. **Status distribution**:
   ```sql
   SELECT status, COUNT(*)
   FROM investigations
   GROUP BY status
   ORDER BY COUNT(*) DESC;
   ```

### Dashboard Supabase

1. **Acesse**: https://supabase.com/dashboard/project/pbsiyuattnwgohvkkkks
2. **Reports**: Veja atividade da tabela investigations
3. **Logs**: SQL queries executados

---

## 🐛 Troubleshooting

### Problema 1: "Unauthorized" nos logs

**Causa**: SERVICE_ROLE_KEY incorreto ou expirado

**Solução**:
1. Acesse Supabase Dashboard → Settings → API
2. Copie o `service_role key` (secret)
3. Atualize variável no Railway
4. Redesploy

---

### Problema 2: "relation 'investigations' does not exist"

**Causa**: Migration SQL não foi rodada

**Solução**:
```bash
# 1. Acesse Supabase SQL Editor
# 2. Copie conteúdo de: migrations/supabase/001_create_investigations_table.sql
# 3. Execute todo o SQL
# 4. Verifique: SELECT * FROM investigations LIMIT 1;
```

---

### Problema 3: Investigações não aparecem no Supabase

**Checklist**:
- ✅ Variáveis adicionadas nos 3 serviços (API, Worker, Beat)?
- ✅ Railway redesployou com sucesso?
- ✅ Logs da API mostram "Using Supabase REST service"?
- ✅ Celery Beat está rodando? (veja logs do serviço cidadao-beat)
- ✅ Migration SQL foi executada no Supabase?

---

### Problema 4: RLS bloqueia investigações automáticas

**Causa**: Policy muito restritiva

**Solução**:
```sql
-- Adicione exceção para sistema
CREATE POLICY "System auto monitor access"
ON investigations FOR ALL
USING (user_id = 'system_auto_monitor')
WITH CHECK (user_id = 'system_auto_monitor');
```

---

## ✅ Checklist de Configuração

Use esta lista para validar que tudo está correto:

### Railway (3 serviços)
- [ ] **cidadao-api**: SUPABASE_URL configurado
- [ ] **cidadao-api**: SUPABASE_SERVICE_ROLE_KEY configurado
- [ ] **cidadao-api**: SUPABASE_ANON_KEY configurado (opcional)
- [ ] **cidadao-worker**: SUPABASE_URL configurado
- [ ] **cidadao-worker**: SUPABASE_SERVICE_ROLE_KEY configurado
- [ ] **cidadao-worker**: SUPABASE_ANON_KEY configurado (opcional)
- [ ] **cidadao-beat**: SUPABASE_URL configurado
- [ ] **cidadao-beat**: SUPABASE_SERVICE_ROLE_KEY configurado
- [ ] **cidadao-beat**: SUPABASE_ANON_KEY configurado (opcional)

### Supabase
- [ ] Migration SQL executada (001_create_investigations_table.sql)
- [ ] Tabela `investigations` existe
- [ ] RLS policies configuradas
- [ ] SERVICE_ROLE_KEY copiado corretamente

### Validação
- [ ] Logs do Railway mostram "Using Supabase REST service"
- [ ] Teste manual de criação de investigação funciona
- [ ] Dados aparecem no Supabase Table Editor
- [ ] Auto-investigations sendo criadas (checar user_id = 'system_auto_monitor')

---

## 🎯 Resultado Esperado

Após seguir este guia, você terá:

1. ✅ **Persistência completa**: Investigações salvas no Supabase PostgreSQL
2. ✅ **Auto-investigations funcionando**: Celery Beat cria investigações a cada 30min
3. ✅ **Dados preservados**: Mesmo após restart dos containers Railway
4. ✅ **Histórico completo**: Todas as investigações desde a configuração
5. ✅ **Monitoramento**: Dashboards Supabase com métricas reais

---

## 📚 Referências

- **Supabase Dashboard**: https://supabase.com/dashboard/project/pbsiyuattnwgohvkkkks
- **Railway Dashboard**: https://railway.app
- **API Docs**: https://cidadao-api-production.up.railway.app/docs
- **Migration SQL**: `/migrations/supabase/001_create_investigations_table.sql`
- **Service Selector**: `/src/services/investigation_service_selector.py`

---

**Configuração documentada por**: Anderson Henrique da Silva
**Data**: 2025-10-09 09:35:00 -03:00
**Localização**: Minas Gerais, Brasil

*Mantendo a transparência com dados persistentes* 🚀
