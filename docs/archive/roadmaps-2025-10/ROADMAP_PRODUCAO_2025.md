# 🚀 Roadmap de Produção - Cidadão.AI Backend

**Autor**: Anderson Henrique da Silva
**Data**: 2025-10-16
**Objetivo**: Colocar o backend em produção no Railway com investigações reais e persistência em banco de dados

---

## 📊 Estado Atual (Análise Completa)

### ✅ O que ESTÁ Funcionando

1. **Sistema Multi-Agente**: 17/17 agentes operacionais (100%)
2. **APIs de Investigação**: Endpoints completos com SSE streaming
3. **Geração de Relatórios**: Sistema completo com múltiplos formatos
4. **Supabase**: Configurado e pronto (REST API implementada)
5. **Docker Compose**: Production stack configurado
6. **Railway CLI**: Instalado (v4.10.0)
7. **Alembic Migrations**: 5 migrations criadas
8. **30+ APIs de Transparência**: IBGE, DataSUS, INEP, TCEs, CKAN

### ❌ O que PRECISA ser Configurado

1. **GROQ_API_KEY**: Atualmente placeholder (`your-groq-api-key-here`)
2. **Railway Authentication**: Precisa fazer login
3. **Database**: Usando SQLite local (migrar para PostgreSQL)
4. **In-Memory Storage**: Investigações e relatórios em memória
5. **Frontend Integration**: Testar com Next.js

---

## 🎯 Roadmap em 5 Fases

### **FASE 1: Preparação Local (1-2 horas)** ⏱️

#### 1.1. Configurar API Keys Reais

```bash
# Editar .env
nano .env

# Adicionar/Atualizar:
GROQ_API_KEY=<sua-api-key-real-do-groq>  # Obter em: https://console.groq.com
```

**Verificação**:
```bash
# Testar conexão com LLM
python -c "from src.core.config import settings; print(f'GROQ: {settings.groq_api_key[:20]}...')"
```

#### 1.2. Testar Sistema Localmente

```bash
# 1. Instalar dependências
make install-dev

# 2. Rodar migrations (Supabase)
make db-upgrade

# 3. Iniciar servidor
JWT_SECRET_KEY=test SECRET_KEY=test make run-dev
```

**Endpoints para Testar**:
```bash
# Health check
curl http://localhost:8000/health

# API info
curl http://localhost:8000/api/v1/info

# Federal APIs (sem auth)
curl http://localhost:8000/api/v1/federal/ibge/states
```

#### 1.3. Testar Investigação Real (Local)

```bash
# Criar usuário de teste via API
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@cidadao.ai",
    "password": "teste123",
    "full_name": "Teste Usuario"
  }'

# Fazer login e pegar JWT token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teste@cidadao.ai",
    "password": "teste123"
  }' | jq -r '.access_token')

# Iniciar investigação real
curl -X POST http://localhost:8000/api/v1/investigations/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Contratos de saúde acima de R$ 1 milhão",
    "data_source": "contracts",
    "anomaly_types": ["price", "vendor", "temporal"]
  }'

# Pegar investigation_id da resposta e consultar status
curl http://localhost:8000/api/v1/investigations/{investigation_id}/status \
  -H "Authorization: Bearer $TOKEN"
```

**Validação**: Investigação deve processar dados reais das APIs federais.

---

### **FASE 2: Railway Setup (2-3 horas)** 🚂

#### 2.1. Autenticar no Railway

```bash
# Login no Railway
railway login

# Verificar autenticação
railway whoami
```

#### 2.2. Criar Projeto e Serviços

```bash
# Criar novo projeto
railway init

# Criar serviços necessários
railway add --service postgres  # PostgreSQL database
railway add --service redis     # Redis cache (opcional)
```

**Configuração do PostgreSQL**:
- Railway cria automaticamente o database
- Pega a `DATABASE_URL` gerada

```bash
# Ver variáveis de ambiente
railway variables
```

#### 2.3. Configurar Variáveis de Ambiente

```bash
# Setar variáveis críticas
railway variables set GROQ_API_KEY=<sua-key>
railway variables set JWT_SECRET_KEY=$(python scripts/generate_secrets.py jwt)
railway variables set SECRET_KEY=$(python scripts/generate_secrets.py secret)

# Setar Supabase (já configurado)
railway variables set SUPABASE_URL=https://pbsiyuattnwgohvkkkks.supabase.co
railway variables set SUPABASE_SERVICE_ROLE_KEY=<key-do-.env>
railway variables set SUPABASE_ANON_KEY=<key-do-.env>

# Dados.gov.br (já configurado)
railway variables set DADOS_GOV_API_KEY=<key-do-.env>
railway variables set TRANSPARENCY_API_KEY=<key-do-.env>

# Environment
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set PYTHONUNBUFFERED=1

# CORS (ajustar para URL do frontend)
railway variables set BACKEND_CORS_ORIGINS='["https://seu-frontend.vercel.app","http://localhost:3000"]'
```

#### 2.4. Conectar Database

**Opção A: Usar Railway PostgreSQL** (Recomendado)
```bash
# DATABASE_URL já está setada automaticamente pelo Railway
# Apenas verificar:
railway variables | grep DATABASE_URL
```

**Opção B: Usar Supabase PostgreSQL**
```bash
# Usar a connection string do .env
railway variables set DATABASE_URL="postgresql://postgres:12356890%21%21%40%40Cidadao@db.pbsiyuattnwgohvkkkks.supabase.co:5432/postgres"
```

#### 2.5. Rodar Migrations

```bash
# Conectar ao Railway e rodar migrations
railway run make db-upgrade

# OU via Railway CLI direto
railway run alembic upgrade head
```

---

### **FASE 3: Deploy Inicial (1 hora)** 🚀

#### 3.1. Preparar para Deploy

```bash
# Verificar railway.json
cat railway.json

# Deve estar assim:
# {
#   "$schema": "https://railway.app/railway.schema.json",
#   "build": {
#     "builder": "NIXPACKS"
#   },
#   "deploy": {
#     "restartPolicyType": "ON_FAILURE",
#     "restartPolicyMaxRetries": 10
#   }
# }
```

#### 3.2. Criar Procfile (se não existir)

```bash
# Verificar se existe
cat Procfile

# Se não, criar:
cat > Procfile << 'EOF'
web: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
EOF
```

#### 3.3. Deploy!

```bash
# Deploy para Railway
railway up

# Acompanhar logs
railway logs

# Verificar status
railway status
```

**URL do Deploy**: Railway vai gerar uma URL automática:
```
https://cidadao-ai-backend-production.up.railway.app
```

#### 3.4. Testar Deploy

```bash
# Pegar URL do Railway
RAILWAY_URL=$(railway domain)

# Health check
curl $RAILWAY_URL/health

# API info
curl $RAILWAY_URL/api/v1/info

# Federal APIs
curl $RAILWAY_URL/api/v1/federal/ibge/states
```

---

### **FASE 4: Persistência em Banco (2-3 horas)** 💾

#### 4.1. Validar Supabase Integration

O código já está preparado para usar Supabase REST API via `investigation_service_selector.py`:

```python
# src/services/investigation_service_selector.py
# Seleciona automaticamente:
# - Supabase REST API (HuggingFace/Railway)
# - Supabase PostgreSQL direto (local)
# - In-memory fallback
```

**Testar persistência**:
```bash
# Criar investigação (deve salvar no Supabase)
curl -X POST $RAILWAY_URL/api/v1/investigations/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Test persistência",
    "data_source": "contracts"
  }'

# Verificar no Supabase Dashboard:
# https://app.supabase.com/project/pbsiyuattnwgohvkkkks/editor
# Tabela: investigations
```

#### 4.2. Migrar Relatórios para DB (Se Necessário)

Atualmente relatórios estão em `_active_reports` (in-memory).

**Opção 1: Criar Migration para Reports**
```bash
# Criar migration
make migrate
# Mensagem: "add_reports_table"

# Editar: alembic/versions/XXX_add_reports_table.py
# Adicionar:
# - id, user_id, title, report_type, status
# - content, metadata, word_count
# - created_at, updated_at
```

**Opção 2: Usar Supabase Storage para PDFs/HTMLs**
```python
# src/services/report_service.py
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Upload PDF to Supabase Storage
supabase.storage.from_("reports").upload(
    f"{report_id}.pdf",
    pdf_bytes
)
```

#### 4.3. Testar Cache (Opcional - Redis)

```bash
# Se habilitou Redis no Railway
railway variables set REDIS_URL=<railway-redis-url>

# Testar
redis-cli -u $REDIS_URL ping
# Deve retornar: PONG
```

---

### **FASE 5: Integração com Frontend (2-3 horas)** 🎨

#### 5.1. Documentação de Endpoints para Frontend

**Criar arquivo para o time de frontend**:

```bash
cat > docs/FRONTEND_INTEGRATION.md << 'EOF'
# Frontend Integration Guide

## Base URL
**Production**: https://cidadao-ai-backend-production.up.railway.app
**Development**: http://localhost:8000

## Authentication

### Register
POST /api/v1/auth/register
```json
{
  "email": "usuario@exemplo.com",
  "password": "senha123",
  "full_name": "Nome Usuario"
}
```

### Login
POST /api/v1/auth/login
```json
{
  "username": "usuario@exemplo.com",
  "password": "senha123"
}
```
Response: `{ "access_token": "...", "token_type": "bearer" }`

## Investigations

### Start Investigation
POST /api/v1/investigations/start
Headers: `Authorization: Bearer <token>`
```json
{
  "query": "Contratos de saúde acima de R$ 1 milhão",
  "data_source": "contracts",
  "anomaly_types": ["price", "vendor", "temporal"],
  "include_explanations": true,
  "stream_results": false
}
```
Response: `{ "investigation_id": "uuid", "status": "started" }`

### Get Investigation Status
GET /api/v1/investigations/{investigation_id}/status
Headers: `Authorization: Bearer <token>`

### Stream Investigation Results (SSE)
GET /api/v1/investigations/stream/{investigation_id}
Headers: `Authorization: Bearer <token>`

**SSE Events**:
- `data: {"type": "progress", "progress": 0.5, ...}`
- `data: {"type": "anomaly", "result": {...}}`
- `data: {"type": "completion", "status": "completed"}`

### Get Complete Results
GET /api/v1/investigations/{investigation_id}/results
Headers: `Authorization: Bearer <token>`

## Reports

### Generate Report
POST /api/v1/reports/generate
Headers: `Authorization: Bearer <token>`
```json
{
  "report_type": "executive_summary",
  "title": "Relatório Mensal",
  "data_sources": ["investigations"],
  "investigation_ids": ["uuid1", "uuid2"],
  "time_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "output_format": "html",
  "target_audience": "executive"
}
```
Response: `{ "report_id": "uuid", "status": "started" }`

### Get Report Status
GET /api/v1/reports/{report_id}/status
Headers: `Authorization: Bearer <token>`

### Get Report
GET /api/v1/reports/{report_id}
Headers: `Authorization: Bearer <token>`

### Download Report
GET /api/v1/reports/{report_id}/download?format=pdf
Headers: `Authorization: Bearer <token>`

## Federal APIs (Public - No Auth)

### Get Brazilian States
GET /api/v1/federal/ibge/states

### Get Municipalities
POST /api/v1/federal/ibge/municipalities
```json
{
  "state_code": "33"
}
```

### DataSUS Health Indicators
POST /api/v1/federal/datasus/indicators
```json
{
  "indicator": "mortality_rate",
  "location": "Rio de Janeiro"
}
```
EOF
```

#### 5.2. CORS Configuration

```bash
# Adicionar domínio do frontend no Railway
railway variables set BACKEND_CORS_ORIGINS='[
  "https://cidadao-frontend.vercel.app",
  "http://localhost:3000",
  "http://localhost:3001"
]'

# Restart service
railway restart
```

#### 5.3. Exemplo de Integração Next.js

**Criar `lib/api-client.ts` no frontend**:

```typescript
// lib/api-client.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function startInvestigation(
  query: string,
  dataSource: string,
  token: string
) {
  const response = await fetch(`${API_URL}/api/v1/investigations/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      query,
      data_source: dataSource,
      anomaly_types: ['price', 'vendor', 'temporal'],
      include_explanations: true
    })
  });

  if (!response.ok) throw new Error('Failed to start investigation');
  return response.json();
}

export function streamInvestigationResults(
  investigationId: string,
  token: string,
  onProgress: (data: any) => void,
  onAnomaly: (data: any) => void,
  onComplete: (data: any) => void
) {
  const eventSource = new EventSource(
    `${API_URL}/api/v1/investigations/stream/${investigationId}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch (data.type) {
      case 'progress':
        onProgress(data);
        break;
      case 'anomaly':
        onAnomaly(data);
        break;
      case 'completion':
        onComplete(data);
        eventSource.close();
        break;
    }
  };

  eventSource.onerror = () => {
    eventSource.close();
  };

  return eventSource;
}

export async function generateReport(
  reportData: any,
  token: string
) {
  const response = await fetch(`${API_URL}/api/v1/reports/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(reportData)
  });

  if (!response.ok) throw new Error('Failed to generate report');
  return response.json();
}

export async function downloadReport(
  reportId: string,
  format: 'pdf' | 'html' | 'markdown' | 'json',
  token: string
) {
  const response = await fetch(
    `${API_URL}/api/v1/reports/${reportId}/download?format=${format}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );

  if (!response.ok) throw new Error('Failed to download report');
  return response.blob();
}
```

#### 5.4. Testar Integração Completa

**Test Flow**:
1. Frontend → Login
2. Frontend → Start Investigation
3. Frontend → Stream Results (SSE)
4. Frontend → Generate Report
5. Frontend → Download PDF

---

## 📋 Checklist de Produção

### Antes do Deploy

- [ ] GROQ_API_KEY configurada
- [ ] JWT_SECRET_KEY gerada (64 caracteres)
- [ ] SECRET_KEY gerada (64 caracteres)
- [ ] Supabase configurado
- [ ] Migrations rodadas localmente
- [ ] Testes passando (`make test`)
- [ ] Railway CLI autenticado
- [ ] CORS configurado para frontend

### Durante o Deploy

- [ ] Railway projeto criado
- [ ] PostgreSQL provisionado
- [ ] Variáveis de ambiente setadas
- [ ] Migrations rodadas em produção
- [ ] Deploy executado (`railway up`)
- [ ] Logs verificados (`railway logs`)
- [ ] Health check passando

### Após o Deploy

- [ ] Teste de investigação real
- [ ] Teste de geração de relatório
- [ ] Persistência no Supabase validada
- [ ] SSE streaming funcionando
- [ ] Frontend integrado e testado
- [ ] Monitoring configurado (Prometheus/Grafana)

---

## 🔧 Troubleshooting

### Erro: "Unauthorized. Please login with `railway login`"
```bash
railway login
railway whoami
```

### Erro: "GROQ_API_KEY not configured"
```bash
railway variables set GROQ_API_KEY=<sua-key>
railway restart
```

### Erro: "Database connection failed"
```bash
# Verificar DATABASE_URL
railway variables | grep DATABASE_URL

# Testar conexão
railway run python -c "from src.infrastructure.database import get_db; print('DB OK')"
```

### Erro: "Supabase REST API failed"
```bash
# Verificar keys
railway variables | grep SUPABASE

# Testar manualmente
curl -X GET https://pbsiyuattnwgohvkkkks.supabase.co/rest/v1/investigations \
  -H "apikey: <SUPABASE_ANON_KEY>" \
  -H "Authorization: Bearer <SUPABASE_SERVICE_ROLE_KEY>"
```

### Investigations não persistem
```bash
# Verificar logs
railway logs --tail 100

# Verificar tabela existe no Supabase
# Dashboard > Table Editor > investigations
```

---

## 📈 Monitoramento em Produção

### Railway Dashboard
- **URL**: https://railway.app/dashboard
- Métricas: CPU, RAM, Network
- Logs em tempo real

### Supabase Dashboard
- **URL**: https://app.supabase.com/project/pbsiyuattnwgohvkkkks
- Database: Queries, Connections
- API: Request logs
- Storage: Files uploaded

### Prometheus + Grafana (Opcional - Local)
```bash
# Rodar monitoring local
make monitoring-up

# Grafana: http://localhost:3000
# User: admin / Pass: cidadao123
```

**Dashboards**:
- Cidadão.AI Overview
- Agents Performance
- Federal APIs Status
- SLO/SLA Tracking

---

## 🎯 Próximos Passos

### Short-term (1-2 semanas)
- [ ] Implementar Celery Worker para background tasks
- [ ] Configurar Celery Beat para auto-investigations
- [ ] Adicionar Flower para monitoring de tasks
- [ ] Implementar cache em Redis (performance)
- [ ] Configurar backup automático do database

### Mid-term (1 mês)
- [ ] Implementar CI/CD com GitHub Actions
- [ ] Adicionar testes E2E com Playwright
- [ ] Configurar alertas no Sentry
- [ ] Implementar rate limiting avançado
- [ ] Adicionar GraphQL endpoint

### Long-term (3 meses)
- [ ] Implementar microservices architecture
- [ ] Adicionar Kubernetes deployment
- [ ] Implementar data lake com BigQuery
- [ ] Machine Learning pipeline em produção
- [ ] Multi-region deployment

---

## 📚 Recursos

### Documentação
- **Railway**: https://docs.railway.app
- **Supabase**: https://supabase.com/docs
- **Groq API**: https://console.groq.com/docs
- **FastAPI**: https://fastapi.tiangolo.com

### Suporte
- **Issues**: GitHub Issues
- **Email**: andersonhs27@gmail.com
- **Discord**: [Cidadão.AI Community]

---

**Status**: 🟢 Ready for Production
**Última Atualização**: 2025-10-16
**Próxima Revisão**: 2025-11-01
