# 🔌 Status Real de Conexão dos Endpoints

**Autor**: Anderson Henrique da Silva  
**Data**: Outubro 2025

## ❌ REALIDADE: Nem todos os endpoints estão conectados!

### 📊 Resumo do Status Real

| Status | Quantidade | Percentual | Descrição |
|--------|------------|------------|-----------|
| ✅ Conectado e Funcionando | ~350 | 68% | Endpoints ativos e respondendo |
| 🔧 Parcialmente Conectado | ~100 | 19% | Estrutura existe mas implementação incompleta |
| ❌ Não Conectado | ~39 | 8% | Arquivos existem mas não estão no app.py |
| ⚠️ Bloqueado Externamente | ~30 | 5% | Portal da Transparência (403) |

## ❌ Arquivos de Rotas NÃO CONECTADOS

Estes arquivos existem mas **NÃO estão importados** em `app.py`:

### 1. **webhooks.py** - Webhooks para eventos externos
```python
# ARQUIVO EXISTE MAS NÃO ESTÁ CONECTADO!
# Endpoints definidos mas inacessíveis:
POST /api/v1/webhooks/incoming/github
POST /api/v1/webhooks/incoming/slack  
POST /api/v1/webhooks/register
GET  /api/v1/webhooks/
DELETE /api/v1/webhooks/{webhook_id}
```

### 2. **monitoring.py** - Monitoramento avançado SLO/SLA
```python
# NÃO CONECTADO
GET /api/v1/monitoring/slo
GET /api/v1/monitoring/sla
POST /api/v1/monitoring/alerts
```

### 3. **chaos.py** - Engenharia do caos
```python
# NÃO CONECTADO
POST /api/v1/chaos/latency
POST /api/v1/chaos/failure
POST /api/v1/chaos/cpu-spike
```

### 4. **debug.py** - Ferramentas de debug
```python
# NÃO CONECTADO
GET /api/v1/debug/routes
GET /api/v1/debug/config
GET /api/v1/debug/memory
```

### 5. **auth_db.py** - Autenticação com banco de dados
```python
# NÃO CONECTADO - usando auth em memória
POST /api/v1/auth/db/register
POST /api/v1/auth/db/login
```

## 🔧 Endpoints PARCIALMENTE Conectados

### 1. **Investigations** - Conectado mas retorna erro
```python
# PROBLEMA: Retorna "temporariamente indisponível"
POST /api/v1/investigations/start  # ❌ Sempre retorna erro
```

### 2. **WebSocket** - Estrutura existe mas não funciona
```python
# PROBLEMA: Implementação incompleta
WS /api/v1/ws/chat  # 🔧 Não processa mensagens corretamente
```

### 3. **GraphQL** - Endpoint existe mas schema incompleto
```python
# PROBLEMA: Schema GraphQL não definido
POST /graphql  # 🔧 Retorna erro de schema
```

### 4. **Alguns Agentes** - Estrutura sem implementação
```python
# Agentes que existem mas não têm lógica:
POST /api/v1/agents/dandara      # 🔧 Stub apenas
POST /api/v1/agents/lampiao      # 🔧 Stub apenas  
POST /api/v1/agents/niemeyer     # 🔧 Stub apenas
```

## ⚠️ Portal da Transparência - Bloqueios Externos

### Funcionando (22%)
```
✅ /contratos - Requer codigoOrgao
✅ /servidores - Apenas busca por CPF
✅ /orgaos - Informações básicas
```

### Bloqueados pelo Governo (78%)
```
❌ /despesas - Retorna 403
❌ /fornecedores - Retorna 403
❌ /emendas-parlamentares - Retorna 403
❌ /beneficios - Retorna 403
❌ /salarios - Retorna 403
```

## 🚀 Como Conectar os Endpoints Faltantes

### 1. Para conectar os arquivos não registrados:

```python
# Em src/api/app.py, adicionar:

# Importar os routers
from src.api.routes import webhooks, monitoring, chaos, debug

# Registrar no app
app.include_router(
    webhooks.router,
    prefix="/api/v1",
    tags=["Webhooks"]
)

app.include_router(
    monitoring.router,
    prefix="/api/v1",
    tags=["Monitoring SLO/SLA"]
)

# etc...
```

### 2. Para corrigir investigations:

```python
# O problema está na linha 273 do chat.py:
# "Enhanced Zumbi temporarily disabled"
# Já corrigimos isso mas precisa testar
```

### 3. Para implementar WebSocket:

```python
# Implementar handlers reais em websocket_chat.py
# Adicionar lógica de processamento de mensagens
```

## 📋 Prioridades de Conexão

### 🔴 Alta Prioridade
1. **Webhooks** - Necessário para integrações
2. **Monitoring SLO/SLA** - Importante para produção
3. **WebSocket completo** - Para real-time

### 🟡 Média Prioridade  
1. **GraphQL schema** - API alternativa
2. **Agentes faltantes** - Completar os 17
3. **Debug endpoints** - Útil para desenvolvimento

### 🟢 Baixa Prioridade
1. **Chaos engineering** - Para testes avançados
2. **Auth DB** - Sistema atual funciona

## 🧪 Como Verificar Status Real

```bash
# 1. Listar todas as rotas registradas
curl http://localhost:8000/openapi.json | jq '.paths | keys'

# 2. Testar endpoint específico
curl -X POST http://localhost:8000/api/v1/webhooks/test
# Se retornar 404, não está conectado!

# 3. Verificar arquivo app.py
grep -n "include_router" src/api/app.py | wc -l
# Deve mostrar quantos routers estão conectados
```

## 📊 Conclusão

- **490 endpoints** estão tecnicamente "disponíveis"
- Mas apenas **~350 funcionam de verdade**
- **39 endpoints** existem mas não estão conectados
- **~100 endpoints** estão parcialmente implementados
- **Portal da Transparência** tem limitações externas

Para ter TODOS funcionando, precisamos:
1. Conectar os arquivos não registrados
2. Completar implementações parciais
3. Corrigir endpoints com erro
4. Aceitar limitações do Portal da Transparência