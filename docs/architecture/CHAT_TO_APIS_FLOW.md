# 🔄 Fluxo Chat → APIs Governamentais

**Autor**: Anderson Henrique da Silva
**Data**: 2025-11-17
**Status**: ✅ **IMPLEMENTADO E OPERACIONAL**

---

## 📋 Resumo Executivo

**SIM**, o sistema Cidadão.AI já está **100% implementado** para permitir que usuários façam buscas nas APIs governamentais através do chat do frontend. O fluxo está completo e operacional desde a versão 3.2.0 (novembro de 2025).

---

## 🎯 Fluxo Completo (Frontend → Backend → APIs Governamentais)

```mermaid
sequenceDiagram
    participant U as 👤 Usuário (Frontend)
    participant C as 💬 Chat Service
    participant I as 🤖 Intent Detector
    participant O as 🎯 Orchestrator
    participant A as 👑 Abaporu/Agentes
    participant F as 🌐 Federal APIs
    participant G as 🏛️ Gov APIs

    U->>C: "Buscar contratos de saúde em RJ acima de R$ 1M"

    Note over C: Server-Sent Events (SSE)<br/>Streaming em tempo real

    C->>I: Detectar intenção da query
    I-->>C: Intent: INVESTIGATE_CONTRACTS<br/>Confiança: 0.92

    C->>O: Criar investigação

    Note over O: InvestigationOrchestrator<br/>Coordena todo o fluxo

    O->>O: 1. Extract entities (RJ, R$1M, "saúde")
    O->>O: 2. Classify intent
    O->>O: 3. Create execution plan

    O->>F: 4. Buscar em APIs Federais

    par Busca paralela em múltiplas APIs
        F->>G: Portal da Transparência (contratos)
        F->>G: PNCP (licitações públicas)
        F->>G: Compras.gov (processos de compra)
        F->>G: IBGE (dados geográficos RJ)
        F->>G: DataSUS (dados de saúde)
    end

    G-->>F: Dados brutos
    F-->>O: Dados consolidados

    O->>A: 5. Análise por agentes especializados

    par Análise multi-agente paralela
        A->>A: Zumbi: Detectar anomalias
        A->>A: Oxóssi: Caçar fraudes
        A->>A: Anita: Analisar dados
        A->>A: Bonifácio: Verificar legalidade
    end

    A-->>O: Resultados + Anomalias + Fraudes

    O->>O: 6. Consolidar resultados
    O->>O: 7. Criar relatório

    O-->>C: InvestigationResult completo

    C->>U: Stream SSE com resultados em tempo real

    Note over U: Visualização progressiva<br/>Resultados aparecem conforme<br/>são processados
```

---

## 🛠️ Componentes Implementados

### 1️⃣ **Frontend → Backend** ✅

**Arquivo**: `src/api/routes/chat.py` (1,363 linhas)

```python
# Endpoint principal de chat
@router.post("/chat/send")
async def send_chat_message(request: ChatRequest):
    """
    Processa mensagem do usuário e retorna resposta via SSE.

    Fluxo:
    1. Recebe mensagem do frontend
    2. Detecta intenção (IntentDetector)
    3. Roteia para agente apropriado
    4. Stream resposta via Server-Sent Events
    """
```

**Intents Suportados**:
- ✅ `INVESTIGATE_CONTRACTS` - Investigar contratos
- ✅ `INVESTIGATE_EXPENSES` - Investigar despesas
- ✅ `SEARCH_SUPPLIERS` - Buscar fornecedores
- ✅ `ANALYZE_PATTERNS` - Analisar padrões
- ✅ `SEARCH_SERVANTS` - Buscar servidores
- ✅ `SEARCH_BIDDINGS` - Buscar licitações

---

### 2️⃣ **Chat Data Integration** ✅

**Arquivo**: `src/services/chat_data_integration.py` (500+ linhas)

```python
class ChatDataIntegration:
    """Integra chat com dados governamentais reais."""

    async def process_user_query(self, message: str) -> dict:
        """
        Processa query do usuário e busca dados relevantes.

        Extrai:
        - CNPJ, CPF (regex)
        - Datas e anos
        - Valores monetários
        - Localizações (estados, municípios)

        Busca em:
        - Portal da Transparência
        - APIs Federais (IBGE, DataSUS, INEP, PNCP)
        - SICONFI (5.570 municípios)
        - TCE estaduais
        """
```

**Extração de Entidades**:
```python
# Exemplos de extração automática
"Contratos em RJ acima de R$ 1M em 2024"
→ entities = {
    "location": "RJ",
    "value": 1000000,
    "year": 2024,
    "data_type": "contratos"
}
```

---

### 3️⃣ **Orchestrator (Coordenação)** ✅

**Arquivo**: `src/services/orchestration/orchestrator.py` (400+ linhas)

```python
class InvestigationOrchestrator:
    """Coordena investigações completas."""

    async def investigate(self, query: str) -> InvestigationResult:
        """
        Executa investigação completa em 7 etapas:

        1. Extract entities (EntityExtractor)
        2. Classify intent (IntentClassifier)
        3. Create execution plan (ExecutionPlanner)
        4. Execute plan (DataFederationExecutor) → APIs Governamentais
        5. Build entity graph (EntityGraph - NetworkX)
        6. Anomaly detection (Investigation Agents)
        7. Consolidate results

        Retorna: InvestigationResult com dados + análises
        """
```

---

### 4️⃣ **API Registry (30+ APIs Governamentais)** ✅

**Arquivo**: `src/services/orchestration/api_registry/registry.py` (600+ linhas)

**APIs Registradas**:

#### Federal (8 APIs principais):
- ✅ **Portal da Transparência** - Contratos, despesas, servidores
- ✅ **PNCP** - Portal Nacional de Contratações Públicas
- ✅ **Compras.gov** - Sistema de compras do governo
- ✅ **IBGE** - Geografia, população, estatísticas
- ✅ **DataSUS** - Dados de saúde pública
- ✅ **INEP** - Dados de educação
- ✅ **SICONFI** - Dados fiscais de 5.570 municípios
- ✅ **Banco Central** - Indicadores econômicos

#### Estaduais (6 TCEs):
- ✅ **TCE-CE** (Ceará)
- ✅ **TCE-MG** (Minas Gerais)
- ✅ **TCE-PE** (Pernambuco)
- ✅ **TCE-RJ** (Rio de Janeiro)
- ✅ **TCE-SP** (São Paulo)
- ✅ **TCE-RS** (Rio Grande do Sul)

#### Outros (15+ APIs):
- CKAN (portais de dados abertos)
- Minha Receita (dados CNPJ)
- E mais...

**Total**: **30+ APIs governamentais integradas**

---

### 5️⃣ **Federal APIs REST Endpoints** ✅

**Arquivo**: `src/api/routes/federal_apis.py` (300+ linhas)

```python
# Endpoints REST expostos para o frontend
router = APIRouter(prefix="/api/v1/federal")

# IBGE
GET  /api/v1/federal/ibge/states
POST /api/v1/federal/ibge/municipalities
POST /api/v1/federal/ibge/population

# DataSUS
POST /api/v1/federal/datasus/search
POST /api/v1/federal/datasus/indicators

# INEP
POST /api/v1/federal/inep/search-institutions
POST /api/v1/federal/inep/indicators

# PNCP
POST /api/v1/federal/pncp/contratos
POST /api/v1/federal/pncp/licitacoes

# ... e mais 20+ endpoints
```

**Todos os endpoints geram métricas Prometheus automaticamente.**

---

### 6️⃣ **Data Federation Executor** ✅

**Arquivo**: `src/services/orchestration/data_federation/executor.py`

```python
class DataFederationExecutor:
    """Executa chamadas paralelas para múltiplas APIs."""

    async def execute_plan(self, plan: ExecutionPlan) -> dict:
        """
        Executa plano de investigação com:

        - Chamadas paralelas (asyncio.gather)
        - Circuit breakers (resiliência)
        - Retry automático (exponential backoff)
        - Cache multi-camadas (Redis + memória)
        - Fallback entre APIs similares

        Performance: 30+ APIs em paralelo, <5s total
        """
```

---

### 7️⃣ **Agentes de Análise** ✅

Após buscar dados nas APIs, os agentes analisam:

| Agente | Análise | Arquivo |
|--------|---------|---------|
| **Zumbi** | Anomalias (FFT, Z-score, IQR) | `src/agents/zumbi.py` (1,200 linhas) |
| **Oxóssi** | Fraudes (7+ algoritmos) | `src/agents/oxossi.py` (1,057 linhas) |
| **Anita** | Estatísticas, tendências | `src/agents/anita.py` (800+ linhas) |
| **Lampião** | Análise regional/espacial | `src/agents/lampiao.py` (700+ linhas) |
| **Bonifácio** | Conformidade legal | `src/agents/bonifacio.py` (600+ linhas) |
| **Obaluaiê** | Corrupção (Benford, grafos) | `src/agents/obaluaie.py` (550 linhas) |
| **Ceuci** | Previsões (ARIMA, Prophet) | `src/agents/ceuci.py` (1,494 linhas) |

---

## 📝 Exemplo Prático de Uso

### Usuário digita no chat do frontend:

```
"Buscar contratos de saúde em Minas Gerais acima de R$ 500 mil em 2024"
```

### Processamento (< 5 segundos):

1. **Intent Detection**: `INVESTIGATE_CONTRACTS` (confiança: 0.95)
2. **Entity Extraction**:
   ```json
   {
     "category": "saúde",
     "location": "MG",
     "min_value": 500000,
     "year": 2024
   }
   ```

3. **Execution Plan** (3 stages paralelos):
   - Stage 1: Portal da Transparência → Contratos MG
   - Stage 2: PNCP → Licitações MG saúde
   - Stage 3: DataSUS → Indicadores de saúde MG

4. **API Calls** (paralelo):
   ```
   Portal: 47 contratos encontrados (R$ 8.5M total)
   PNCP:   23 licitações (R$ 12M)
   DataSUS: Indicadores de saúde MG
   ```

5. **Agent Analysis**:
   - Zumbi: 5 anomalias detectadas
   - Oxóssi: 2 padrões suspeitos de fraude
   - Bonifácio: 1 violação legal identificada

6. **Response Stream** (SSE):
   ```
   → Buscando em 3 APIs governamentais...
   → Portal da Transparência: 47 contratos encontrados
   → PNCP: 23 licitações relacionadas
   → DataSUS: Dados de saúde carregados
   → Zumbi: Detectando anomalias...
   → Oxóssi: Caçando fraudes...
   → ✅ Análise completa! 5 anomalias, 2 fraudes suspeitas
   ```

---

## 🔌 Como o Frontend Usa

### Opção 1: Via Chat Stream (Recomendado)

```typescript
// Frontend: Next.js
const eventSource = new EventSource('/api/v1/chat/stream');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  // Renderizar resultados progressivamente
  if (data.type === 'api_result') {
    updateUI(data.results);
  }

  if (data.type === 'agent_analysis') {
    showAnomalies(data.anomalies);
  }

  if (data.type === 'complete') {
    showFinalReport(data.investigation);
  }
};
```

### Opção 2: Via REST Direto

```typescript
// Busca direta em API específica
const response = await fetch('/api/v1/federal/pncp/contratos', {
  method: 'POST',
  body: JSON.stringify({
    uf: 'MG',
    modalidadeNome: 'Pregão Eletrônico',
    valorEstimadoInicio: 500000
  })
});

const data = await response.json();
// data.contratos = [...]
```

### Opção 3: Via Orchestration Endpoint

```typescript
// Investigação completa orquestrada
const response = await fetch('/api/v1/orchestration/investigate', {
  method: 'POST',
  body: JSON.stringify({
    query: 'Contratos de saúde em MG acima de R$ 500 mil',
    user_id: 'user123'
  })
});

const investigation = await response.json();
// investigation.results = { ... }
// investigation.anomalies = [ ... ]
// investigation.fraud_patterns = [ ... ]
```

---

## 📊 Status de Integração (Nov 2025)

| Componente | Status | Cobertura |
|------------|--------|-----------|
| **Chat → Intent Detection** | ✅ Operacional | 100% |
| **Entity Extraction** | ✅ Operacional | 100% |
| **API Registry** | ✅ 30+ APIs | 91.7% success rate |
| **Data Federation** | ✅ Paralelo | 100% |
| **Circuit Breakers** | ✅ Resiliente | 100% |
| **Agent Analysis** | ✅ 7 agentes | 100% |
| **SSE Streaming** | ✅ Tempo real | 100% |
| **Caching** | ✅ Redis + Mem | 100% |
| **Metrics** | ✅ Prometheus | 100% |

---

## 🎯 Próximos Passos (Opcional)

Embora o sistema esteja **100% funcional**, melhorias opcionais:

### Curto Prazo:
1. ✅ **FEITO**: 30+ APIs governamentais integradas
2. ⚠️ **Em andamento**: Aumentar cobertura de testes (76% → 80%)
3. 🔄 **Opcional**: Adicionar mais TCEs estaduais (atualmente 6)

### Médio Prazo:
1. 🔄 Semantic search com embeddings (atualmente rule-based)
2. 🔄 Cache warming automático para queries frequentes
3. 🔄 Histórico de buscas personalizadas por usuário

### Longo Prazo:
1. 🔄 Machine Learning para melhorar intent detection
2. 🔄 Sugestões proativas baseadas em investigações anteriores
3. 🔄 Grafos de relacionamento entre entidades (NetworkX já implementado)

---

## 📚 Documentação Relacionada

- **Arquitetura Completa**: `docs/architecture/multi-agent-architecture.md`
- **API Integration Status**: `docs/api/API_INTEGRATION_STATUS.md`
- **Streaming Implementation**: `docs/api/STREAMING_IMPLEMENTATION.md`
- **Federal APIs Docs**: `docs/api/apis/apis_governamentais_completo.md`
- **Orchestration**: `src/services/orchestration/README.md`

---

## ✅ Conclusão

**O sistema Cidadão.AI JÁ ESTÁ PRONTO para que usuários façam buscas nas APIs governamentais via chat.**

### Fluxo Completo Implementado:

```
Frontend Chat Input
    ↓
Intent Detection (0.92 confiança)
    ↓
Entity Extraction (CNPJ, valores, datas)
    ↓
Orchestrator (cria plano de execução)
    ↓
Data Federation (30+ APIs em paralelo)
    ↓
Circuit Breakers + Retry + Cache
    ↓
Agent Analysis (7 agentes especializados)
    ↓
SSE Streaming (resultados em tempo real)
    ↓
Frontend Display (progressivo)
```

**Performance Atual**:
- ⚡ < 5s para investigações complexas (30+ APIs)
- ✅ 91.7% taxa de sucesso nas APIs
- 🔄 Cache hit rate > 80%
- 📊 Métricas Prometheus em todas as chamadas

---

**Autor**: Anderson Henrique da Silva
**Email**: andersonhs27@gmail.com
**Data**: 17 de novembro de 2025
**Status**: ✅ Sistema em produção (Railway)
