# 🗺️ Mapa Completo de Endpoints da API Cidadão.AI

**Última atualização**: Janeiro 2025  
**Total de endpoints**: 529 endpoints  
**Status**: 490 ativos, 39 inativos

## 📊 Resumo por Categoria

| Categoria | Endpoints Ativos | Status |
|-----------|------------------|---------|
| Health & Monitoring | 6 | ✅ Funcionando |
| Authentication | 7 | ✅ Funcionando |
| Chat | 7 | ✅ Funcionando |
| Agents | 11 | ✅ Funcionando (8/17 agentes) |
| Investigations | 6 | ✅ Funcionando |
| Analysis | 4 | ✅ Funcionando |
| Reports | 4 | ✅ Funcionando |
| Dados.gov.br | 8 | ✅ Funcionando |
| Portal Transparência | - | ⚠️ 22% funcionando |
| Admin | 23 | ✅ Funcionando |
| WebSocket | 2 | 🔧 Parcial |
| GraphQL | 2 | 🔧 Parcial |

## 🔌 Endpoints Ativos e Conectados

### 1. Health & Monitoring (`/health/*`)
```
✅ GET  /health/                    - Health check básico
✅ GET  /health/detailed            - Health check detalhado
✅ GET  /health/live               - Kubernetes liveness probe
✅ GET  /health/ready              - Kubernetes readiness probe  
✅ GET  /health/metrics            - Métricas Prometheus
✅ GET  /health/metrics/json       - Métricas em JSON
```

### 2. Autenticação (`/auth/*`)
```
✅ POST /auth/register             - Registro de usuário
✅ POST /auth/login               - Login
✅ POST /auth/refresh             - Renovar token JWT
✅ GET  /auth/me                  - Dados do usuário atual
✅ POST /auth/logout              - Logout
✅ POST /auth/oauth/google        - OAuth Google
✅ POST /auth/oauth/github        - OAuth GitHub
```

### 3. Chat - MÚLTIPLAS IMPLEMENTAÇÕES (`/api/v1/chat/*`)
```
✅ POST /api/v1/chat/message       - Chat principal (com Zumbi + dados.gov.br)
✅ POST /api/v1/chat/stream       - Chat com streaming
✅ POST /api/v1/chat/simple       - Chat simples (Maritaca AI)
✅ POST /api/v1/chat/stable       - Chat estável
✅ POST /api/v1/chat/optimized    - Chat otimizado
✅ POST /api/v1/chat/emergency    - Chat emergência (fallback)
✅ GET  /api/v1/chat/history      - Histórico de conversas
```

### 4. Agentes de IA (`/api/v1/agents/*`)
```
✅ POST /api/v1/agents/invoke      - Invocar agente genérico
✅ GET  /api/v1/agents/            - Listar agentes disponíveis
✅ GET  /api/v1/agents/status      - Status de todos os agentes

Agentes Específicos:
✅ POST /api/v1/agents/zumbi       - Zumbi dos Palmares (detecção de anomalias)
✅ POST /api/v1/agents/anita       - Anita Garibaldi (análise de padrões)
✅ POST /api/v1/agents/tiradentes  - Tiradentes (geração de relatórios)
✅ POST /api/v1/agents/bonifacio   - José Bonifácio (compliance)
✅ POST /api/v1/agents/maria-quiteria - Maria Quitéria (auditoria)
✅ POST /api/v1/agents/drummond    - Carlos Drummond (conversacional)
✅ POST /api/v1/agents/senna       - Ayrton Senna (roteamento)
✅ POST /api/v1/agents/machado     - Machado de Assis (narrativas)
```

### 5. Investigações (`/api/v1/investigations/*`)
```
✅ POST   /api/v1/investigations/start     - Iniciar investigação
✅ GET    /api/v1/investigations/stream/{id} - Stream de resultados (SSE)
✅ GET    /api/v1/investigations/{id}/status - Status da investigação
✅ GET    /api/v1/investigations/{id}/results - Resultados completos
✅ GET    /api/v1/investigations/          - Listar investigações
✅ DELETE /api/v1/investigations/{id}      - Cancelar investigação
```

### 6. Análises (`/api/v1/analysis/*`)
```
✅ POST /api/v1/analysis/patterns     - Análise de padrões
✅ POST /api/v1/analysis/correlations - Correlações
✅ POST /api/v1/analysis/trends       - Tendências
✅ POST /api/v1/analysis/efficiency   - Métricas de eficiência
```

### 7. Relatórios (`/api/v1/reports/*`)
```
✅ POST /api/v1/reports/generate      - Gerar relatório
✅ GET  /api/v1/reports/{id}         - Obter relatório
✅ GET  /api/v1/reports/             - Listar relatórios
✅ POST /api/v1/reports/schedule     - Agendar relatório
```

### 8. Dados.gov.br - NOVA INTEGRAÇÃO (`/api/v1/dados-gov/*`)
```
✅ GET  /api/v1/dados-gov/search              - Buscar datasets
✅ GET  /api/v1/dados-gov/dataset/{id}        - Detalhes do dataset
✅ GET  /api/v1/dados-gov/resource/{id}/url   - URL do recurso
✅ GET  /api/v1/dados-gov/organizations       - Listar organizações
✅ POST /api/v1/dados-gov/search/transparency - Buscar dados transparência
✅ GET  /api/v1/dados-gov/analyze/{topic}     - Analisar disponibilidade
✅ GET  /api/v1/dados-gov/spending-data       - Dados de gastos
✅ GET  /api/v1/dados-gov/procurement-data    - Dados de licitações
```

### 9. Exportação (`/api/v1/export/*`)
```
✅ POST /api/v1/export/csv         - Exportar para CSV
✅ POST /api/v1/export/json        - Exportar para JSON
✅ POST /api/v1/export/pdf         - Exportar para PDF
✅ POST /api/v1/export/markdown    - Exportar para Markdown
```

### 10. Administração (`/api/v1/admin/*`)

#### Gestão de IP Whitelist
```
✅ GET    /api/v1/admin/ip-whitelist      - Listar IPs
✅ POST   /api/v1/admin/ip-whitelist      - Adicionar IP
✅ DELETE /api/v1/admin/ip-whitelist/{ip} - Remover IP
```

#### Gestão de Cache
```
✅ POST /api/v1/admin/cache/warm   - Aquecer cache
✅ POST /api/v1/admin/cache/clear  - Limpar cache
✅ GET  /api/v1/admin/cache/stats  - Estatísticas
```

#### Otimização de Banco de Dados
```
✅ POST /api/v1/admin/db/optimize  - Otimizar DB
✅ POST /api/v1/admin/db/vacuum    - Vacuum DB
✅ GET  /api/v1/admin/db/stats     - Estatísticas
```

#### Compressão
```
✅ GET  /api/v1/admin/compression/stats    - Estatísticas
✅ POST /api/v1/admin/compression/settings - Configurações
```

#### Pools de Conexão
```
✅ GET  /api/v1/admin/pools/stats  - Estatísticas
✅ POST /api/v1/admin/pools/reset  - Reiniciar pools
```

#### Lazy Loading de Agentes
```
✅ GET  /api/v1/admin/agents/memory   - Uso de memória
✅ POST /api/v1/admin/agents/preload  - Pré-carregar
✅ POST /api/v1/admin/agents/unload   - Descarregar
```

### 11. Gestão de API Keys (`/api/v1/api-keys/*`)
```
✅ POST   /api/v1/api-keys/        - Criar API key
✅ GET    /api/v1/api-keys/        - Listar API keys
✅ DELETE /api/v1/api-keys/{id}    - Revogar API key
```

### 12. WebSocket
```
🔧 WS /api/v1/ws/chat              - Chat em tempo real
🔧 WS /api/v1/ws/investigations    - Investigações em tempo real
```

### 13. Operações em Lote (`/api/v1/batch/*`)
```
✅ POST /api/v1/batch/investigations - Investigações em lote
✅ POST /api/v1/batch/analysis      - Análises em lote
✅ GET  /api/v1/batch/{id}/status   - Status do lote
```

### 14. GraphQL
```
🔧 POST /graphql                   - Endpoint GraphQL
🔧 GET  /graphql                   - GraphQL Playground
```

### 15. Notificações (`/api/v1/notifications/*`)
```
✅ POST /api/v1/notifications/subscribe - Inscrever
✅ POST /api/v1/notifications/send      - Enviar
✅ GET  /api/v1/notifications/          - Listar
```

### 16. Métricas (`/api/v1/metrics/*`)
```
✅ GET /api/v1/metrics/agents      - Métricas dos agentes
✅ GET /api/v1/metrics/system      - Métricas do sistema
✅ GET /api/v1/metrics/business    - Métricas de negócio
```

### 17. Visualização (`/api/v1/visualization/*`)
```
✅ POST /api/v1/visualization/chart     - Gerar gráfico
✅ POST /api/v1/visualization/dashboard - Criar dashboard
✅ GET  /api/v1/visualization/templates - Templates
```

### 18. Dados Geográficos (`/api/v1/geographic/*`)
```
✅ GET  /api/v1/geographic/states       - Estados
✅ GET  /api/v1/geographic/cities/{uf}  - Cidades
✅ POST /api/v1/geographic/heatmap      - Mapa de calor
```

## ⚠️ Portal da Transparência - Status Limitado

### Endpoints Funcionando (22%)
```
✅ Contratos - Requer parâmetro codigoOrgao
✅ Servidores - Busca apenas por CPF
✅ Órgãos - Informações das organizações
```

### Endpoints Bloqueados (78% retornam 403)
```
❌ Despesas
❌ Fornecedores  
❌ Emendas parlamentares
❌ Benefícios
❌ Dados de salários/remuneração
```

## 🔧 Rotas Não Registradas (Arquivos existem mas não estão ativos)

1. **auth_db.py** - Autenticação com banco de dados
2. **chaos.py** - Engenharia do caos
3. **chat_debug.py** - Debug do chat
4. **debug.py** - Endpoints de debug
5. **monitoring.py** - Monitoramento avançado (SLO/SLA)
6. **webhooks.py** - Webhooks
7. **websocket.py** - WebSocket adicional

## 📈 Próximos Passos para Conectar Tudo

### 1. Ativar Rotas Não Registradas
```python
# Em src/api/app.py, adicionar:
from src.api.routes import webhooks, monitoring, debug
app.include_router(webhooks.router, prefix="/api/v1/webhooks")
app.include_router(monitoring.router, prefix="/api/v1/monitoring")
app.include_router(debug.router, prefix="/api/v1/debug")
```

### 2. Completar Integrações WebSocket
- Implementar streaming real-time para investigações
- Adicionar notificações push via WebSocket

### 3. Finalizar GraphQL
- Completar schema GraphQL
- Adicionar resolvers para todas as entidades

### 4. Melhorar Taxa de Sucesso do Portal da Transparência
- Investigar alternativas para endpoints bloqueados
- Implementar cache agressivo para dados disponíveis
- Adicionar fallback para dados sintéticos em desenvolvimento

## 🚀 Como Testar Todos os Endpoints

```bash
# 1. Instalar dependências de teste
pip install httpie

# 2. Testar saúde da API
http GET localhost:8000/health/

# 3. Criar usuário e fazer login
http POST localhost:8000/auth/register email=test@example.com password=senha123
http POST localhost:8000/auth/login email=test@example.com password=senha123

# 4. Testar chat com investigação
http POST localhost:8000/api/v1/chat/message \
  message="Investigar contratos suspeitos do Ministério da Saúde" \
  Authorization:"Bearer $TOKEN"

# 5. Buscar dados no dados.gov.br
http GET localhost:8000/api/v1/dados-gov/search \
  query=saúde \
  Authorization:"Bearer $TOKEN"
```

## 📱 Endpoints Mais Importantes para Frontend

1. **Chat Principal**: `POST /api/v1/chat/message`
2. **Investigações**: `POST /api/v1/investigations/start`
3. **Relatórios**: `POST /api/v1/reports/generate`
4. **Exportação**: `POST /api/v1/export/pdf`
5. **Dados Abertos**: `GET /api/v1/dados-gov/search`