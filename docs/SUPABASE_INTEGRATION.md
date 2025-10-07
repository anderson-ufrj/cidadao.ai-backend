# Integração com Supabase

Este documento descreve como configurar e usar a integração com Supabase para armazenamento centralizado de investigações.

## 📋 Visão Geral

O **Cidadão.AI Backend** agora suporta Supabase como banco de dados central, permitindo que:

1. **Backend** armazene resultados de investigações diretamente no Supabase
2. **Frontend** consuma os dados em tempo real via Supabase Client
3. **Row Level Security (RLS)** garanta que usuários só vejam suas próprias investigações
4. **Realtime Subscriptions** permitam atualizações em tempo real no frontend

## 🔧 Configuração

### 1. Setup no Supabase Dashboard

#### 1.1 Criar Projeto
1. Acesse [Supabase Dashboard](https://app.supabase.com)
2. Crie um novo projeto ou use um existente
3. Aguarde a criação do banco PostgreSQL

#### 1.2 Executar Migration
1. Vá para **SQL Editor** no dashboard
2. Copie o conteúdo de `migrations/supabase/001_create_investigations_table.sql`
3. Execute a migration
4. Verifique se a tabela `investigations` foi criada

#### 1.3 Obter Credenciais
1. Vá para **Settings > API**
2. Copie as seguintes informações:
   - **Project URL**: `https://[project-id].supabase.co`
   - **Anon Key**: Para acesso público (com RLS)
   - **Service Role Key**: Para backend (bypass RLS)

3. Vá para **Settings > Database > Connection string**
4. Copie a **URI** de conexão PostgreSQL

### 2. Configuração do Backend

#### 2.1 Variáveis de Ambiente

Adicione ao `.env`:

```bash
# Supabase PostgreSQL Connection
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres

# Supabase API Keys (opcional - para Row Level Security)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Connection Pool Settings (opcional)
SUPABASE_MIN_CONNECTIONS=5
SUPABASE_MAX_CONNECTIONS=20
```

**Importante**: Use `SUPABASE_SERVICE_ROLE_KEY` para que o backend possa escrever dados sem RLS.

#### 2.2 HuggingFace Spaces

No HuggingFace Spaces, adicione as variáveis em **Settings > Variables**:

```
SUPABASE_DB_URL: postgresql://postgres:...
SUPABASE_SERVICE_ROLE_KEY: eyJhbGci...
```

### 3. Instalação de Dependências

```bash
# Já incluído em requirements.txt
pip install asyncpg>=0.29.0
```

## 🚀 Uso no Backend

### Exemplo 1: Criar Investigação

```python
from src.services.investigation_service_supabase import investigation_service_supabase

# Criar investigação
investigation = await investigation_service_supabase.create(
    user_id="user-uuid-from-auth",
    query="Contratos com valores acima de R$ 1 milhão",
    data_source="contracts",
    filters={"min_value": 1000000},
    anomaly_types=["price", "vendor"],
)

print(f"Investigation ID: {investigation['id']}")
```

### Exemplo 2: Executar Investigação

```python
# Executar em background
await investigation_service_supabase.start_investigation(
    investigation_id=investigation['id']
)

# A investigação roda em background e atualiza o Supabase
# O frontend pode monitorar via realtime subscription
```

### Exemplo 3: Consultar Investigações

```python
# Listar investigações do usuário
investigations = await investigation_service_supabase.search(
    user_id="user-uuid",
    status="completed",
    limit=10
)

for inv in investigations:
    print(f"{inv['id']}: {inv['query']} - {inv['status']}")
```

## 🌐 Uso no Frontend (Next.js)

### 1. Setup do Supabase Client

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### 2. Listar Investigações do Usuário

```typescript
// pages/investigations.tsx
import { supabase } from '@/lib/supabase'

export async function getInvestigations() {
  const { data, error } = await supabase
    .from('investigations')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(10)

  if (error) {
    console.error('Error fetching investigations:', error)
    return []
  }

  return data
}
```

### 3. Monitorar Investigação em Tempo Real

```typescript
// components/InvestigationMonitor.tsx
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'

export function InvestigationMonitor({ investigationId }: { investigationId: string }) {
  const [investigation, setInvestigation] = useState<any>(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    // Fetch initial state
    const fetchInvestigation = async () => {
      const { data } = await supabase
        .from('investigations')
        .select('*')
        .eq('id', investigationId)
        .single()

      setInvestigation(data)
      setProgress(data?.progress || 0)
    }

    fetchInvestigation()

    // Subscribe to real-time updates
    const channel = supabase
      .channel(`investigation:${investigationId}`)
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'investigations',
          filter: `id=eq.${investigationId}`,
        },
        (payload) => {
          console.log('Investigation updated:', payload.new)
          setInvestigation(payload.new)
          setProgress(payload.new.progress || 0)
        }
      )
      .subscribe()

    // Cleanup
    return () => {
      supabase.removeChannel(channel)
    }
  }, [investigationId])

  return (
    <div>
      <h3>Investigation Status: {investigation?.status}</h3>
      <div>Progress: {Math.round(progress * 100)}%</div>
      <div>Phase: {investigation?.current_phase}</div>
      <div>Anomalies Found: {investigation?.anomalies_found || 0}</div>

      {investigation?.status === 'completed' && (
        <div>
          <h4>Results</h4>
          <pre>{JSON.stringify(investigation.results, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
```

### 4. Criar Nova Investigação via API

```typescript
// services/investigationService.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL

export async function createInvestigation(params: {
  query: string
  data_source: string
  filters?: Record<string, any>
  anomaly_types?: string[]
}) {
  // Obter token JWT do usuário
  const { data: { session } } = await supabase.auth.getSession()

  const response = await fetch(`${API_URL}/api/v1/investigations/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session?.access_token}`,
    },
    body: JSON.stringify(params),
  })

  if (!response.ok) {
    throw new Error('Failed to create investigation')
  }

  return await response.json()
}
```

## 📊 Schema da Tabela

### Campos Principais

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | ID único da investigação |
| `user_id` | UUID | ID do usuário (auth.users) |
| `query` | TEXT | Query da investigação |
| `data_source` | VARCHAR | Fonte de dados (contracts, expenses, etc) |
| `status` | VARCHAR | Status: pending, processing, completed, failed, cancelled |
| `progress` | FLOAT | Progresso de 0.0 a 1.0 |
| `current_phase` | VARCHAR | Fase atual (data_retrieval, analysis, etc) |
| `results` | JSONB | Array de anomalias detectadas |
| `summary` | TEXT | Resumo da investigação |
| `confidence_score` | FLOAT | Confiança geral (0.0 a 1.0) |
| `anomalies_found` | INTEGER | Total de anomalias |
| `total_records_analyzed` | INTEGER | Total de registros analisados |

### Exemplo de Result (JSONB)

```json
{
  "anomaly_id": "uuid",
  "type": "price",
  "severity": "high",
  "confidence": 0.92,
  "description": "Preço 45% acima da média",
  "explanation": "Análise de 1.234 contratos similares...",
  "affected_records": [
    {
      "contract_id": "123",
      "value": 1500000,
      "expected_value": 1034000
    }
  ],
  "suggested_actions": [
    "Solicitar justificativa do preço",
    "Comparar com licitações similares"
  ],
  "metadata": {
    "analysis_method": "fft_spectral",
    "comparison_count": 1234
  }
}
```

## 🔒 Segurança (Row Level Security)

### Políticas Ativas

1. **SELECT**: Usuários só veem suas próprias investigações
2. **INSERT**: Usuários só criam investigações para si mesmos
3. **UPDATE**: Usuários só atualizam suas próprias investigações
4. **DELETE**: Usuários só deletam suas próprias investigações
5. **Service Role**: Backend com `service_role_key` pode gerenciar tudo

### Testando RLS

```sql
-- Como usuário autenticado
SELECT * FROM investigations; -- Vê apenas suas investigações

-- Como service_role (backend)
-- Vê todas as investigações
```

## 🐛 Troubleshooting

### Erro: "Connection refused"

Verifique se `SUPABASE_DB_URL` está correto:
```bash
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres"
```

### Erro: "Permission denied"

- Verifique se RLS está habilitado
- Use `SUPABASE_SERVICE_ROLE_KEY` no backend
- Verifique se `user_id` corresponde ao `auth.uid()`

### Investigação não atualiza no frontend

- Verifique se Realtime está habilitado no Supabase
- Vá para **Database > Replication** e habilite `investigations`
- Verifique se o frontend tem a subscription correta

## 📈 Monitoramento

### Ver estatísticas do usuário

```sql
SELECT * FROM get_investigation_stats('user-uuid');
```

### Ver investigações ativas

```sql
SELECT id, query, status, progress, current_phase
FROM investigations
WHERE status IN ('pending', 'processing')
ORDER BY created_at DESC;
```

### Performance indexes

A migration cria 7 indexes otimizados:
- `user_id` (B-tree)
- `status` (B-tree)
- `created_at` (B-tree desc)
- `user_id, status` (composite)
- `filters` (GIN - JSONB)
- `results` (GIN - JSONB)

## 🚢 Deploy

### HuggingFace Spaces

```bash
# Adicione as variáveis no dashboard
SUPABASE_DB_URL=postgresql://...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# O app.py vai usar automaticamente
```

### Docker

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - SUPABASE_DB_URL=${SUPABASE_DB_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
```

## 📚 Recursos

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)

## ✅ Checklist de Implementação

- [x] Criar serviço `SupabaseService`
- [x] Criar `InvestigationServiceSupabase`
- [x] Criar migration SQL
- [x] Documentar configuração
- [ ] Executar migration no Supabase
- [ ] Configurar variáveis de ambiente
- [ ] Testar criação de investigação
- [ ] Testar realtime no frontend
- [ ] Deploy no HuggingFace Spaces
