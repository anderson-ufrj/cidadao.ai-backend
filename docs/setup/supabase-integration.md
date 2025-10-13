# 🗄️ Integração Backend ↔ Supabase ↔ Frontend

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## 📋 Resumo da Solução

Implementei uma **integração completa com Supabase** para que o backend e frontend compartilhem o mesmo banco de dados PostgreSQL, permitindo:

✅ **Backend FastAPI** armazena resultados de investigações diretamente no Supabase
✅ **Frontend Next.js** consome dados em tempo real via Supabase Client
✅ **Row Level Security (RLS)** garante isolamento de dados por usuário
✅ **Realtime Subscriptions** atualiza UI automaticamente durante processamento
✅ **Single Source of Truth** - um único banco para toda a aplicação

---

## 🏗️ Arquitetura Implementada

```
┌─────────────────────────────────────────────────────────────┐
│                        USUÁRIO                              │
└────────┬─────────────────────────────────────┬──────────────┘
         │                                     │
         ▼                                     ▼
┌──────────────────┐                 ┌──────────────────────┐
│   Frontend       │                 │   Backend            │
│   (Next.js)      │◄────REST API────│   (FastAPI)          │
│                  │                 │                      │
│  + Supabase JS   │                 │  + SupabaseService   │
│  + Realtime      │                 │  + AsyncPG Pool      │
│  + RLS (anon)    │                 │  + Service Role Key  │
└────────┬─────────┘                 └──────────┬───────────┘
         │                                      │
         │         ┌─────────────────────┐     │
         └────────►│   SUPABASE          │◄────┘
                   │   (PostgreSQL)      │
                   │                     │
                   │  investigations ✓   │
                   │  + 7 indexes        │
                   │  + 5 RLS policies   │
                   │  + Realtime enabled │
                   │  + Triggers         │
                   └─────────────────────┘
```

### Fluxo de Dados

1. **Frontend** envia request para Backend via API REST
2. **Backend** cria investigação no Supabase
3. **Agentes AI** processam investigação e atualizam progresso no Supabase
4. **Frontend** recebe updates em tempo real via Supabase Realtime
5. **Resultados** disponíveis imediatamente para ambos

---

## 📦 Arquivos Criados

```
cidadao.ai-backend/
├── src/
│   └── services/
│       ├── supabase_service.py                # ✨ Serviço de integração Supabase
│       └── investigation_service_supabase.py  # ✨ InvestigationService adaptado
│
├── migrations/
│   └── supabase/
│       └── 001_create_investigations_table.sql # ✨ Schema completo
│
├── scripts/
│   └── test_supabase_connection.py            # ✨ Script de validação
│
├── docs/
│   ├── SUPABASE_INTEGRATION.md                # ✨ Documentação completa
│   └── SUPABASE_QUICK_START.md                # ✨ Guia rápido (5 min)
│
├── examples/
│   └── frontend_integration.tsx               # ✨ Exemplo completo React/Next.js
│
├── .env.supabase.example                      # ✨ Template de variáveis
└── README_SUPABASE.md                         # ✨ Este arquivo
```

---

## 🚀 Como Usar

### 1. Setup Rápido (5 minutos)

Siga o guia: **[docs/SUPABASE_QUICK_START.md](docs/SUPABASE_QUICK_START.md)**

### 2. Setup Detalhado

Leia a documentação completa: **[docs/SUPABASE_INTEGRATION.md](docs/SUPABASE_INTEGRATION.md)**

### 3. Quick Commands

```bash
# 1. Configurar variáveis
cp .env.supabase.example .env
# Edite .env com suas credenciais

# 2. Testar conexão
python scripts/test_supabase_connection.py

# 3. Executar migration no Supabase Dashboard
# Copie migrations/supabase/001_create_investigations_table.sql
# Cole no SQL Editor do Supabase

# 4. Usar no código
from src.services.investigation_service_supabase import investigation_service_supabase

# Criar investigação
inv = await investigation_service_supabase.create(
    user_id="user-uuid",
    query="Contratos suspeitos",
    data_source="contracts"
)
```

---

## 🔑 Variáveis de Ambiente Necessárias

### Backend (.env)

```bash
# OBRIGATÓRIO
SUPABASE_DB_URL=postgresql://postgres:SENHA@db.pbsiyuattnwgohvkkkks.supabase.co:5432/postgres

# RECOMENDADO (para bypass RLS no backend)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# OPCIONAL
SUPABASE_MIN_CONNECTIONS=5
SUPABASE_MAX_CONNECTIONS=20
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_SUPABASE_URL=https://pbsiyuattnwgohvkkkks.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
NEXT_PUBLIC_API_URL=https://neural-thinker-cidadao-ai-backend.hf.space
```

### HuggingFace Spaces

Adicione em **Settings > Variables**:
- `SUPABASE_DB_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

---

## 📊 Schema do Banco de Dados

### Tabela: `investigations`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | PK, gerado automaticamente |
| `user_id` | UUID | FK para auth.users (Supabase Auth) |
| `query` | TEXT | Query da investigação |
| `data_source` | VARCHAR | contracts, expenses, etc |
| `status` | VARCHAR | pending → processing → completed |
| `progress` | FLOAT | 0.0 a 1.0 |
| `current_phase` | VARCHAR | Fase atual (data_retrieval, analysis...) |
| `results` | JSONB | Array de anomalias detectadas |
| `summary` | TEXT | Resumo gerado pelo agente |
| `confidence_score` | FLOAT | Confiança geral (0.0 a 1.0) |
| `anomalies_found` | INTEGER | Total de anomalias |
| `total_records_analyzed` | INTEGER | Total de registros |
| `filters` | JSONB | Filtros aplicados |
| `anomaly_types` | JSONB | Tipos de anomalias buscados |
| `created_at` | TIMESTAMPTZ | Auto-gerado |
| `updated_at` | TIMESTAMPTZ | Auto-atualizado via trigger |
| `started_at` | TIMESTAMPTZ | Quando começou processamento |
| `completed_at` | TIMESTAMPTZ | Quando terminou |

### Índices Criados (7)

1. `idx_investigations_user_id` - B-tree em user_id
2. `idx_investigations_status` - B-tree em status
3. `idx_investigations_created_at` - B-tree DESC em created_at
4. `idx_investigations_user_status` - Composto (user_id, status)
5. `idx_investigations_session_id` - B-tree em session_id
6. `idx_investigations_filters` - GIN em filters (JSONB)
7. `idx_investigations_results` - GIN em results (JSONB)

### Row Level Security (5 Policies)

1. **SELECT**: Users can view their own investigations
2. **INSERT**: Users can create their own investigations
3. **UPDATE**: Users can update their own investigations
4. **DELETE**: Users can delete their own investigations
5. **ALL**: Service role can manage all investigations (backend)

---

## 💻 Exemplos de Código

### Backend: Criar e Processar Investigação

```python
from src.services.investigation_service_supabase import investigation_service_supabase

# 1. Criar investigação
investigation = await investigation_service_supabase.create(
    user_id="user-uuid-from-jwt",
    query="Contratos acima de R$ 1 milhão em 2024",
    data_source="contracts",
    filters={"min_value": 1000000, "year": 2024},
    anomaly_types=["price", "vendor", "temporal"],
)

print(f"Investigation ID: {investigation['id']}")

# 2. Iniciar processamento (background)
await investigation_service_supabase.start_investigation(
    investigation_id=investigation['id']
)

# O agente system processa e atualiza o Supabase automaticamente
# Frontend recebe updates via Realtime
```

### Frontend: Monitorar em Tempo Real

```typescript
import { useInvestigation } from '@/hooks/useInvestigations'

function InvestigationMonitor({ id }: { id: string }) {
  const { investigation, loading } = useInvestigation(id)

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <h2>{investigation?.query}</h2>
      <p>Status: {investigation?.status}</p>
      <p>Progress: {Math.round((investigation?.progress || 0) * 100)}%</p>
      <p>Phase: {investigation?.current_phase}</p>
      <p>Anomalies: {investigation?.anomalies_found}</p>

      {investigation?.status === 'completed' && (
        <div>
          <h3>Results</h3>
          {investigation.results.map(anomaly => (
            <AnomalyCard key={anomaly.anomaly_id} anomaly={anomaly} />
          ))}
        </div>
      )}
    </div>
  )
}
```

### Frontend: Realtime Subscription

```typescript
useEffect(() => {
  // Subscribe to investigation updates
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
        console.log('Update received:', payload.new)
        setInvestigation(payload.new)
      }
    )
    .subscribe()

  return () => {
    supabase.removeChannel(channel)
  }
}, [investigationId])
```

---

## 🔒 Segurança

### Row Level Security (RLS)

✅ **Ativo por padrão** - Usuários só veem suas próprias investigações
✅ **Backend usa service_role_key** - Pode escrever para qualquer usuário
✅ **Frontend usa anon_key** - Respeita RLS automaticamente

### Testando RLS

```sql
-- No SQL Editor do Supabase
-- Simular usuário autenticado
SET LOCAL jwt.claims.sub = 'user-uuid';

-- Esta query só retorna investigações deste usuário
SELECT * FROM investigations;
```

### Políticas RLS Ativas

```sql
-- Ver políticas criadas
SELECT schemaname, tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE tablename = 'investigations';
```

---

## 📈 Performance

### Connection Pooling

```python
# Configurado automaticamente
SUPABASE_MIN_CONNECTIONS=5   # Mínimo mantido aberto
SUPABASE_MAX_CONNECTIONS=20  # Máximo permitido
```

Supabase Free Tier: até 60 conexões simultâneas
Supabase Pro: até 200+ conexões

### Índices Otimizados

- **B-tree** para queries por user_id, status, created_at
- **GIN (JSONB)** para pesquisa dentro de filters e results
- **Composite** para queries combinadas (user_id + status)

### Cache Strategy

```python
# Layer 1: Memory (5 min)
# Layer 2: Redis (1 hr) - opcional
# Layer 3: Supabase (persistent)
```

---

## 🧪 Testes

### Script de Validação

```bash
python scripts/test_supabase_connection.py
```

Verifica:
- ✅ Conexão com Supabase
- ✅ Tabela `investigations` existe
- ✅ RLS está habilitado
- ✅ Policies estão ativas
- ✅ CRUD operations funcionam

### Teste Manual via SQL

```sql
-- Criar investigação de teste
INSERT INTO investigations (user_id, query, data_source, status)
VALUES (
  '00000000-0000-0000-0000-000000000000',
  'Test investigation',
  'contracts',
  'pending'
);

-- Ver investigações
SELECT id, query, status, progress, created_at
FROM investigations
ORDER BY created_at DESC;

-- Atualizar progresso
UPDATE investigations
SET progress = 0.5, current_phase = 'processing'
WHERE id = 'investigation-uuid';
```

---

## 🚢 Deploy

### HuggingFace Spaces

1. Vá para **Settings > Variables**
2. Adicione:
   ```
   SUPABASE_DB_URL=postgresql://...
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
   ```
3. Reinicie o Space
4. Verificar logs: `Starting Cidadão.AI... Connected to Supabase`

### Docker

```yaml
# docker-compose.yml
services:
  backend:
    image: cidadao-ai-backend
    environment:
      - SUPABASE_DB_URL=${SUPABASE_DB_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
    ports:
      - "8000:8000"
```

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| `Connection refused` | Verifique `SUPABASE_DB_URL`, teste com `psql` |
| `Permission denied` | Use `SUPABASE_SERVICE_ROLE_KEY` no backend |
| `Table does not exist` | Execute migration no SQL Editor |
| `Realtime not updating` | Habilite Realtime para tabela no dashboard |
| `Too many connections` | Ajuste `MAX_CONNECTIONS` ou upgrade plano |

Veja mais em: [docs/SUPABASE_INTEGRATION.md#troubleshooting](docs/SUPABASE_INTEGRATION.md)

---

## 📚 Recursos

### Documentação
- [SUPABASE_QUICK_START.md](docs/SUPABASE_QUICK_START.md) - Setup em 5 minutos
- [SUPABASE_INTEGRATION.md](docs/SUPABASE_INTEGRATION.md) - Guia completo
- [frontend_integration.tsx](examples/frontend_integration.tsx) - Exemplos React

### Links Externos
- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [asyncpg](https://magicstack.github.io/asyncpg/)

### Seu Projeto
- **Supabase Dashboard**: https://pbsiyuattnwgohvkkkks.supabase.co
- **Backend API**: https://neural-thinker-cidadao-ai-backend.hf.space
- **Frontend**: (adicionar URL quando deployado)

---

## ✅ Próximos Passos

1. **Executar migration** no Supabase SQL Editor
2. **Configurar variáveis** de ambiente (.env)
3. **Testar conexão** com script
4. **Atualizar código** para usar `investigation_service_supabase`
5. **Deploy** no HuggingFace Spaces com novas variáveis
6. **Configurar frontend** com Supabase Client
7. **Testar fluxo completo** (create → process → monitor)

---

## 🎉 Benefícios da Integração

✅ **Persistência Real** - Dados não se perdem ao reiniciar backend
✅ **Realtime** - Frontend atualiza automaticamente
✅ **Escalabilidade** - Supabase gerencia infraestrutura
✅ **Segurança** - RLS protege dados por usuário
✅ **Backup Automático** - Supabase faz backup diário
✅ **Single Source of Truth** - Um banco para tudo
✅ **Zero Config** - Funciona out-of-the-box após setup inicial

---

**Autor**: Anderson H. Silva
**Data**: 2025-01-07
**Versão**: 1.0.0

**Supabase Project**: pbsiyuattnwgohvkkkks.supabase.co
