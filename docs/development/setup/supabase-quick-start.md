# 🚀 Supabase Integration - Quick Start Guide

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## ⚡ Setup Rápido (5 minutos)

### 1️⃣ Executar Migration no Supabase

1. Acesse seu projeto: **https://pbsiyuattnwgohvkkkks.supabase.co**
2. Vá para **SQL Editor**
3. Clique em **+ New Query**
4. Copie e cole o conteúdo de `migrations/supabase/001_create_investigations_table.sql`
5. Clique em **Run** ▶️
6. Verifique a mensagem de sucesso

### 2️⃣ Obter Credenciais

No seu dashboard Supabase (**pbsiyuattnwgohvkkkks.supabase.co**):

#### Database URL
1. **Settings > Database**
2. Role para baixo até **Connection string**
3. Selecione **URI**
4. Copie a URL (formato: `postgresql://postgres:[PASSWORD]@db.pbsiyuattnwgohvkkkks.supabase.co:5432/postgres`)

#### API Keys
1. **Settings > API**
2. Copie:
   - **Project URL**: `https://pbsiyuattnwgohvkkkks.supabase.co`
   - **anon public**: Para o frontend
   - **service_role**: Para o backend (⚠️ SECRET!)

### 3️⃣ Configurar Backend

Crie/edite o arquivo `.env`:

```bash
# Supabase Database (OBRIGATÓRIO)
SUPABASE_DB_URL=postgresql://postgres:SUA_SENHA@db.pbsiyuattnwgohvkkkks.supabase.co:5432/postgres

# Service Role Key (RECOMENDADO - permite backend escrever sem RLS)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.SUA_SERVICE_ROLE_KEY_AQUI

# Opcional
SUPABASE_MIN_CONNECTIONS=5
SUPABASE_MAX_CONNECTIONS=20
```

### 4️⃣ Testar Conexão

```bash
python scripts/test_supabase_connection.py
```

Você deve ver:
```
✅ Configuration loaded successfully
✅ Connection pool initialized
✅ Health check passed!
✅ Table 'investigations' exists
✅ RLS is enabled
🎉 All tests completed successfully!
```

### 5️⃣ Atualizar Código para Usar Supabase

#### Opção A: Substituir serviço atual

```python
# src/services/__init__.py
# Substitua a importação
from src.services.investigation_service_supabase import investigation_service_supabase as investigation_service

# Agora investigation_service usa Supabase automaticamente
```

#### Opção B: Usar diretamente nas rotas

```python
# src/api/routes/investigations.py
from src.services.investigation_service_supabase import investigation_service_supabase

# Use investigation_service_supabase em vez do serviço antigo
```

### 6️⃣ Configurar Frontend

No seu frontend Next.js, crie `.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://pbsiyuattnwgohvkkkks.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sua-anon-key-aqui
NEXT_PUBLIC_API_URL=https://neural-thinker-cidadao-ai-backend.hf.space
```

Copie o código de exemplo:
```bash
cp examples/frontend_integration.tsx ../cidadao.ai-frontend/hooks/useInvestigations.tsx
```

### 7️⃣ Deploy no HuggingFace Spaces

No HuggingFace Spaces, adicione em **Settings > Variables**:

```
SUPABASE_DB_URL = postgresql://postgres:...
SUPABASE_SERVICE_ROLE_KEY = eyJhbGci...
```

Reinicie o Space.

## 🧪 Testando o Fluxo Completo

### Backend (criar investigação)

```bash
curl -X POST https://neural-thinker-cidadao-ai-backend.hf.space/api/v1/investigations/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_JWT_TOKEN" \
  -d '{
    "query": "Contratos acima de R$ 1 milhão",
    "data_source": "contracts",
    "filters": {"min_value": 1000000},
    "anomaly_types": ["price", "vendor"]
  }'
```

### Frontend (monitorar em tempo real)

```typescript
// components/MyInvestigation.tsx
import { useInvestigation } from '@/hooks/useInvestigations'

function MyInvestigation({ id }: { id: string }) {
  const { investigation } = useInvestigation(id)

  return (
    <div>
      <h2>{investigation?.query}</h2>
      <p>Status: {investigation?.status}</p>
      <p>Progress: {Math.round((investigation?.progress || 0) * 100)}%</p>
      <p>Anomalies: {investigation?.anomalies_found}</p>
    </div>
  )
}
```

## 📊 Verificar Dados no Supabase

### Table Editor
1. Vá para **Table Editor**
2. Selecione tabela `investigations`
3. Veja as investigações criadas em tempo real

### SQL Editor
```sql
-- Ver todas as investigações
SELECT id, user_id, query, status, progress, anomalies_found
FROM investigations
ORDER BY created_at DESC;

-- Ver estatísticas de um usuário
SELECT * FROM get_investigation_stats('user-uuid-aqui');

-- Ver investigações ativas
SELECT * FROM investigations WHERE status IN ('pending', 'processing');
```

## 🔐 Segurança RLS Ativa

✅ **Row Level Security** já está configurado:
- Usuários só veem **suas próprias** investigações
- Backend com `service_role_key` pode escrever para qualquer usuário
- Frontend com `anon_key` respeita RLS automaticamente

Para testar RLS no SQL Editor:
```sql
-- Simular usuário autenticado
SET LOCAL jwt.claims.sub = 'user-uuid-aqui';

-- Esta query só retorna investigações deste usuário
SELECT * FROM investigations;
```

## 🎯 Arquitetura Final

```
┌──────────────┐
│   Frontend   │
│  (Next.js)   │
└──────┬───────┘
       │
       ├─────── Supabase Client (Realtime) ────┐
       │                                        │
       └─────── API REST ───────────────┐      │
                                        │      │
                                        ▼      ▼
                              ┌─────────────────────┐
                              │   Supabase          │
                              │   (PostgreSQL)      │
                              │                     │
                              │  investigations ✓   │
                              │  + RLS policies ✓   │
                              │  + Realtime ✓       │
                              └─────────┬───────────┘
                                        ▲
                                        │
                              ┌─────────┴───────────┐
                              │   Backend FastAPI   │
                              │   (HF Spaces)       │
                              │                     │
                              │  SupabaseService ✓  │
                              │  Multi-agents ✓     │
                              └─────────────────────┘
```

## ✅ Checklist de Implementação

- [ ] Migration executada no Supabase
- [ ] Tabela `investigations` criada
- [ ] RLS habilitado (5 policies ativas)
- [ ] Credenciais copiadas (DB_URL + SERVICE_ROLE_KEY)
- [ ] `.env` configurado no backend
- [ ] Script de teste executado com sucesso
- [ ] Código atualizado para usar `investigation_service_supabase`
- [ ] Variáveis configuradas no HuggingFace Spaces
- [ ] Frontend configurado com Supabase Client
- [ ] Realtime subscription testada
- [ ] Fluxo completo validado (create → process → monitor)

## 🆘 Troubleshooting

### "Connection refused"
```bash
# Teste a conexão diretamente
psql "postgresql://postgres:SENHA@db.pbsiyuattnwgohvkkkks.supabase.co:5432/postgres"
```

### "Permission denied for table investigations"
- Verifique se RLS está habilitado
- Certifique-se de usar `SUPABASE_SERVICE_ROLE_KEY` no backend
- No frontend, usuário deve estar autenticado

### "Table does not exist"
- Execute a migration novamente
- Verifique erros no SQL Editor
- Use `\dt` para listar tabelas no psql

### Investigação não atualiza no frontend
1. **Table Editor > investigations**
2. Clique nos três pontos (⋮)
3. **Edit table**
4. Vá para **Realtime**
5. Habilite **Realtime** para a tabela

## 📚 Próximos Passos

1. **Remover storage in-memory**
   - Deletar `_active_investigations` dict
   - Usar apenas Supabase

2. **Adicionar índices customizados**
   - Baseado em queries mais frequentes
   - Monitorar performance no Supabase

3. **Implementar cache Redis**
   - Para investigações completed
   - TTL de 1 hora

4. **Backup automático**
   - Supabase já faz backup diário
   - Considerar export semanal para S3

5. **Monitoring**
   - Grafana dashboard para métricas Supabase
   - Alertas para conexões esgotadas

## 🎉 Pronto!

Agora você tem:
- ✅ Backend armazenando no Supabase
- ✅ Frontend consumindo em tempo real
- ✅ RLS protegendo dados por usuário
- ✅ Arquitetura escalável
- ✅ Single source of truth

**Supabase Project**: https://pbsiyuattnwgohvkkkks.supabase.co
