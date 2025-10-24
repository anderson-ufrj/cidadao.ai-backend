# 🐘 Railway PostgreSQL + Redis Setup

**Data:** 2025-10-16
**Status:** Migração de Supabase para PostgreSQL nativo do Railway

---

## 🎯 Objetivo

Migrar do Supabase para usar os serviços nativos do Railway:
- **PostgreSQL** - Database principal
- **Redis** - Cache e sessões

## ✅ Serviços Disponíveis no Railway

Você já tem estes serviços configurados:

1. ✅ **Postgres** - PostgreSQL database (via Docker Image)
2. ✅ **cidadao-redis** - Redis cache (via Docker Image)
3. ✅ **cidadao-api** - API principal (via GitHub)
4. ❌ **cidadao.ai-worker** - Celery Worker (FALHANDO - precisa fix)
5. ❌ **cidadao.ai-beat** - Celery Beat (FALHANDO - precisa fix)

---

## 🔧 Configuração de Variáveis

### 1. Variáveis Automáticas do Railway

O Railway já expõe automaticamente estas variáveis quando você adiciona os serviços:

**PostgreSQL:**
```bash
# Railway cria automaticamente (Reference Variables):
DATABASE_URL=postgresql://postgres:${{Postgres.POSTGRES_PASSWORD}}@${{Postgres.RAILWAY_TCP_PROXY_DOMAIN}}:${{Postgres.RAILWAY_TCP_PROXY_PORT}}/railway

# Ou use a variável interna direta:
${{Postgres.DATABASE_URL}}
```

**Redis:**
```bash
# Railway cria automaticamente:
REDIS_URL=redis://default:${{cidadao-redis.REDIS_PASSWORD}}@${{cidadao-redis.RAILWAY_TCP_PROXY_DOMAIN}}:${{cidadao-redis.RAILWAY_TCP_PROXY_PORT}}

# Ou use a variável interna:
${{cidadao-redis.REDIS_URL}}
```

### 2. Variáveis para Configurar no cidadao-api

Vá em **cidadao-api** → **Variables** → **Shared Variables** e atualize:

```bash
# ============================================================================
# DATABASE - PostgreSQL Railway (NOVO - substituindo Supabase)
# ============================================================================
DATABASE_URL=${{Postgres.DATABASE_URL}}

# ============================================================================
# REDIS - Cache Railway (NOVO)
# ============================================================================
REDIS_URL=${{cidadao-redis.REDIS_URL}}

# ============================================================================
# REMOVER VARIÁVEIS DO SUPABASE (não mais necessárias)
# ============================================================================
# SUPABASE_URL=https://pbsiyuattnwgohvkkkks.supabase.co  ❌ REMOVER
# SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...  ❌ REMOVER
# SUPABASE_ANON_KEY=eyJhbGc...  ❌ REMOVER
# SUPABASE_DB_URL=postgresql://...  ❌ REMOVER

# ============================================================================
# LLM PROVIDERS (manter como está)
# ============================================================================
MARITACA_API_KEY=***REMOVED***_22f92d14b8c6e836
MARITACA_MODEL=sabiazinho-3
LLM_PROVIDER=maritaca

ANTHROPIC_API_KEY=***REDACTED-ANTHROPIC-KEY***
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# ============================================================================
# SECURITY (manter como está)
# ============================================================================
JWT_SECRET_KEY=***REMOVED***
SECRET_KEY=***REMOVED***

# ============================================================================
# ENVIRONMENT (manter como está)
# ============================================================================
ENVIRONMENT=production
DEBUG=false

# ============================================================================
# APIS GOVERNAMENTAIS (manter como está)
# ============================================================================
TRANSPARENCY_API_KEY=***REDACTED-TRANSPARENCY-KEY***
DADOS_GOV_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# ============================================================================
# SYSTEM (manter como está)
# ============================================================================
SYSTEM_AUTO_MONITOR_USER_ID=58050609-2fe2-49a6-a342-7cf66d83d216
PYTHONUNBUFFERED=true
APP_ENV=production
```

---

## 🗄️ Schema do PostgreSQL

### Criar Tabela `investigations`

Acesse o PostgreSQL do Railway e execute:

```sql
-- Criar tabela de investigações
CREATE TABLE IF NOT EXISTS investigations (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),

    -- Query e Configuração
    query TEXT NOT NULL,
    data_source VARCHAR(100) NOT NULL,
    filters JSONB DEFAULT '{}'::jsonb,
    anomaly_types JSONB DEFAULT '[]'::jsonb,

    -- Status e Progresso
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    progress FLOAT DEFAULT 0.0,
    current_phase VARCHAR(100),

    -- Resultados
    results JSONB,
    summary TEXT,
    confidence_score FLOAT,
    total_records_analyzed INTEGER,
    anomalies_found INTEGER,

    -- Erro (se falhar)
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    processing_time_ms INTEGER,

    -- Metadados
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_investigations_user_id ON investigations(user_id);
CREATE INDEX IF NOT EXISTS idx_investigations_status ON investigations(status);
CREATE INDEX IF NOT EXISTS idx_investigations_created_at ON investigations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_investigations_session_id ON investigations(session_id) WHERE session_id IS NOT NULL;

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_investigations_updated_at
    BEFORE UPDATE ON investigations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comentários nas colunas
COMMENT ON TABLE investigations IS 'Investigações de transparência pública com resultados de anomalias';
COMMENT ON COLUMN investigations.status IS 'Status: pending, processing, completed, failed, cancelled';
COMMENT ON COLUMN investigations.results IS 'Array JSONB de anomalias detectadas';
COMMENT ON COLUMN investigations.filters IS 'Filtros aplicados na busca (CNPJ, datas, etc)';
```

### Outras Tabelas (Se necessário)

```sql
-- Tabela de usuários (se não tiver)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Tabela de sessões de chat
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Tabela de mensagens de chat
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id),
    role VARCHAR(50) NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

---

## 🔄 Mudanças no Código

### 1. investigation_service_selector.py

✅ **ATUALIZADO** - Agora prioriza PostgreSQL direto:

```python
# Nova ordem de prioridade:
# 1. PostgreSQL direto (Railway, VPS, Local)
# 2. HuggingFace Spaces → Supabase REST API (se disponível)
# 3. Fallback → In-memory (sem persistência)
```

**Log esperado no Railway:**
```
🐘 Using PostgreSQL direct connection for investigations (Railway/VPS)
```

### 2. .env Local (Desenvolvimento)

Atualizar `.env` para testar localmente:

```bash
# PostgreSQL Local ou Railway
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/cidadao_ai

# Redis Local ou Railway
REDIS_URL=redis://localhost:6379/0

# REMOVER (não mais necessário):
# SUPABASE_URL=...
# SUPABASE_SERVICE_ROLE_KEY=...
# SUPABASE_ANON_KEY=...
# SUPABASE_DB_URL=...
```

---

## ✅ Verificação Pós-Configuração

### 1. Verificar Logs do Railway

```bash
# Via Railway Dashboard
https://railway.app/project/56a814f2-e891-4b63-b20f-1dd8f8b356fc/service/cidadao-api

# Procurar por:
✅ "🐘 Using PostgreSQL direct connection for investigations (Railway/VPS)"
✅ "Database connection established"
✅ "Redis connection successful"
```

### 2. Testar Conexão PostgreSQL

```bash
curl -X POST "https://cidadao-api-production.up.railway.app/api/v1/investigations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "query": "Teste de persistência PostgreSQL Railway",
    "data_source": "contracts"
  }'
```

### 3. Verificar Tabela PostgreSQL

Via Railway Dashboard → Postgres → Query:

```sql
SELECT * FROM investigations ORDER BY created_at DESC LIMIT 5;
```

---

## 🐛 Troubleshooting

### Erro: "relation 'investigations' does not exist"

**Solução:** A tabela ainda não foi criada. Execute o schema SQL acima no PostgreSQL do Railway.

### Erro: "connection to database failed"

**Solução:** Verifique se `DATABASE_URL` está configurado corretamente com a referência `${{Postgres.DATABASE_URL}}`.

### Erro: "Redis connection refused"

**Solução:** Verifique se `REDIS_URL` está configurado corretamente com a referência `${{cidadao-redis.REDIS_URL}}`.

### Workers Falhando (Beat e Worker)

**Possíveis causas:**
1. Falta de variável `DATABASE_URL`
2. Falta de variável `REDIS_URL`
3. Dependências faltando

**Solução:** Após configurar DATABASE_URL e REDIS_URL, faça redeploy dos workers.

---

## 📊 Vantagens do PostgreSQL Railway

**vs. Supabase:**

| Característica | Supabase | PostgreSQL Railway |
|----------------|----------|-------------------|
| **Latência** | ~50-100ms | ~5-10ms (mesmo datacenter) |
| **Conexões** | Limitadas no free tier | Mais flexível |
| **Custo** | Separate billing | Incluído no Railway |
| **Complexidade** | REST API overhead | Conexão direta |
| **Performance** | HTTP/HTTPS | TCP nativo |
| **Transações** | Via REST (limitado) | Suporte completo |

**vs. In-memory:**

| Característica | In-memory | PostgreSQL |
|----------------|-----------|------------|
| **Persistência** | ❌ Dados perdidos no restart | ✅ Dados persistentes |
| **Escalabilidade** | ❌ Limitado à RAM | ✅ Escalável |
| **Busca** | ❌ Linear scan | ✅ Índices otimizados |
| **Concorrência** | ❌ Locks em memória | ✅ MVCC PostgreSQL |
| **Backup** | ❌ Impossível | ✅ Backups automáticos |

---

## 🚀 Próximos Passos

1. ✅ **Configurar DATABASE_URL** no Railway → cidadao-api
2. ✅ **Configurar REDIS_URL** no Railway → cidadao-api
3. ✅ **Remover variáveis SUPABASE_*** do Railway
4. ✅ **Criar schema PostgreSQL** (tabela investigations)
5. ✅ **Redeploy da API** para aplicar mudanças
6. ✅ **Testar criação de investigação**
7. ✅ **Verificar persistência** no PostgreSQL
8. ⏳ **Corrigir workers** (Beat e Worker) - mesmo DATABASE_URL/REDIS_URL
9. ⏳ **Configurar backups** automáticos do PostgreSQL

---

**Última Atualização:** 2025-10-16
**Autor:** Anderson Henrique da Silva
