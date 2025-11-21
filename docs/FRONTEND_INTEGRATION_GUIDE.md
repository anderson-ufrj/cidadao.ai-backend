# 📚 GUIA COMPLETO DE INTEGRAÇÃO - FRONTEND CIDADÃO.AI

## 🎯 Visão Geral

O **Backend Cidadão.AI** é uma API REST completa que fornece **TODOS** os dados e funcionalidades necessários para o frontend. O frontend **NÃO** precisa de banco de dados próprio - tudo vem desta API.

### 🔑 Informações Essenciais

```javascript
// Configuração Base
const API_BASE_URL = 'https://cidadao-api-production.up.railway.app'
const API_VERSION = '/api/v1'
const FULL_API_URL = `${API_BASE_URL}${API_VERSION}`

// Headers Padrão
const headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}
```

## 🌐 Endpoints Principais

### 1️⃣ **Health Check & Status**

```javascript
// Verificar se API está online
GET /health/

Response:
{
  "status": "ok",
  "timestamp": "2025-11-21T17:50:00Z",
  "version": "1.0.0",
  "environment": "production"
}
```

### 2️⃣ **Agentes de IA (16 Personagens Históricos)**

Cada agente é um personagem histórico brasileiro com especialidade única:

```javascript
// Listar todos os agentes disponíveis
GET /api/v1/agents/

Response:
{
  "agents": [
    {
      "id": "zumbi",
      "name": "Zumbi dos Palmares",
      "specialty": "Detecção de anomalias",
      "description": "Líder quilombola, detecta irregularidades"
    },
    {
      "id": "anita",
      "name": "Anita Garibaldi",
      "specialty": "Análise de padrões",
      "description": "Revolucionária, analisa tendências"
    },
    // ... mais 14 agentes
  ]
}
```

#### **Invocar Agente Específico**

```javascript
// Exemplo: Analisar contratos com Zumbi
POST /api/v1/agents/zumbi
{
  "query": "Analise contratos de saúde acima de 1 milhão",
  "context": {
    "year": 2024,
    "state": "MG"
  },
  "options": {
    "anomaly_types": ["price", "vendor", "temporal"],
    "threshold": 0.8
  }
}

Response:
{
  "agent": "zumbi_dos_palmares",
  "result": {
    "anomalies": [
      {
        "contract_id": "CTR2024001",
        "type": "price_anomaly",
        "severity": "high",
        "description": "Valor 300% acima da média",
        "value": 5000000,
        "average": 1200000
      }
    ],
    "summary": {
      "total_analyzed": 150,
      "anomalies_found": 12,
      "total_suspicious_value": 45000000
    }
  },
  "metadata": {
    "processing_time": 250,
    "confidence": 0.92
  }
}
```

### 📋 **Lista Completa dos 16 Agentes**

| ID | Nome | Especialidade | Endpoint |
|----|------|---------------|----------|
| `zumbi` | Zumbi dos Palmares | Detecção de anomalias | `/api/v1/agents/zumbi` |
| `anita` | Anita Garibaldi | Análise de padrões | `/api/v1/agents/anita` |
| `tiradentes` | Tiradentes | Geração de relatórios | `/api/v1/agents/tiradentes` |
| `bonifacio` | José Bonifácio | Análise legal | `/api/v1/agents/bonifacio` |
| `maria-quiteria` | Maria Quitéria | Segurança e auditoria | `/api/v1/agents/maria-quiteria` |
| `machado` | Machado de Assis | Análise textual | `/api/v1/agents/machado` |
| `dandara` | Dandara | Equidade social | `/api/v1/agents/dandara` |
| `lampiao` | Lampião | Análise regional | `/api/v1/agents/lampiao` |
| `oscar` | Oscar Niemeyer | Agregação de dados | `/api/v1/agents/oscar` |
| `drummond` | Carlos Drummond | Comunicação | `/api/v1/agents/drummond` |
| `obaluaie` | Obaluaiê | Detecção de corrupção | `/api/v1/agents/obaluaie` |
| `oxossi` | Oxóssi | Busca de dados | `/api/v1/agents/oxossi` |
| `ceuci` | Céuci | Análise preditiva | `/api/v1/agents/ceuci` |
| `abaporu` | Abaporu | Orquestração mestre | `/api/v1/agents/abaporu` |
| `ayrton-senna` | Ayrton Senna | Roteamento semântico | `/api/v1/agents/ayrton-senna` |
| `nana` | Nanã | Gerenciamento de memória | `/api/v1/agents/nana` |

### 3️⃣ **Chat com Streaming (SSE)**

Para conversas em tempo real com respostas progressivas:

```javascript
// Iniciar conversa com streaming
const eventSource = new EventSource(`${API_BASE_URL}/api/v1/chat/stream`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream'
  },
  body: JSON.stringify({
    message: "Encontre contratos suspeitos de obras",
    session_id: "unique-session-id-123"
  })
})

// Receber eventos em tempo real
eventSource.addEventListener('chunk', (event) => {
  const data = JSON.parse(event.data)
  console.log('Partial response:', data.content)
  // Atualizar UI progressivamente
})

eventSource.addEventListener('complete', (event) => {
  const finalResult = JSON.parse(event.data)
  console.log('Investigation complete:', finalResult)
  eventSource.close()
})

eventSource.addEventListener('error', (event) => {
  console.error('Stream error:', event)
  eventSource.close()
})
```

### 4️⃣ **Portal da Transparência - Dados Governamentais**

#### **Contratos Públicos**

```javascript
GET /api/v1/transparency/contracts?year=2024&state=MG&limit=100

Response:
{
  "contracts": [
    {
      "id": "CTR2024001",
      "supplier": "Empresa XYZ Ltda",
      "cnpj": "12.345.678/0001-00",
      "object": "Fornecimento de medicamentos",
      "value": 2500000.00,
      "start_date": "2024-01-15",
      "end_date": "2024-12-31",
      "status": "active",
      "organ": "Secretaria de Saúde",
      "modality": "Pregão Eletrônico",
      "suspicious_flags": ["price_above_average", "single_bidder"]
    }
  ],
  "metadata": {
    "total_count": 1543,
    "total_value": 450000000.00,
    "page": 1,
    "limit": 100
  }
}
```

#### **Servidores Públicos**

```javascript
GET /api/v1/transparency/servants?organ=saude&role=medico

Response:
{
  "servants": [
    {
      "id": "SRV001",
      "name": "João Silva",
      "role": "Médico",
      "organ": "Hospital Municipal",
      "salary": 15000.00,
      "benefits": 3000.00,
      "total_income": 18000.00,
      "admission_date": "2015-03-20",
      "status": "active"
    }
  ],
  "statistics": {
    "average_salary": 14500.00,
    "total_servants": 234,
    "total_cost_monthly": 3393000.00
  }
}
```

#### **Licitações**

```javascript
GET /api/v1/transparency/biddings?status=open&modality=pregao

Response:
{
  "biddings": [
    {
      "id": "PE2024/001",
      "object": "Aquisição de equipamentos hospitalares",
      "estimated_value": 5000000.00,
      "modality": "Pregão Eletrônico",
      "status": "open",
      "opening_date": "2024-12-01T10:00:00",
      "proposals_count": 5,
      "organ": "Secretaria de Saúde"
    }
  ]
}
```

### 5️⃣ **Investigações Automatizadas**

Criar investigações completas que coordenam múltiplos agentes:

```javascript
// Criar nova investigação
POST /api/v1/investigations/
{
  "title": "Investigação de Contratos de TI 2024",
  "description": "Análise completa de contratos de tecnologia",
  "scope": {
    "year": 2024,
    "category": "technology",
    "min_value": 100000
  },
  "agents": ["zumbi", "anita", "tiradentes", "obaluaie"]
}

Response:
{
  "investigation_id": "INV2024-001",
  "status": "processing",
  "estimated_time": 45,
  "created_at": "2024-11-21T18:00:00Z"
}

// Acompanhar progresso
GET /api/v1/investigations/INV2024-001

Response:
{
  "investigation_id": "INV2024-001",
  "status": "completed",
  "progress": 100,
  "findings": {
    "anomalies": 23,
    "patterns": 5,
    "risk_level": "high",
    "total_suspicious_value": 12000000.00
  },
  "agents_results": {
    "zumbi": { /* resultados detalhados */ },
    "anita": { /* resultados detalhados */ },
    "tiradentes": { /* relatório completo */ },
    "obaluaie": { /* indicadores de corrupção */ }
  }
}
```

### 6️⃣ **APIs Federais Integradas**

#### **IBGE - Dados Demográficos**

```javascript
GET /api/v1/federal/ibge/cities?state=MG

Response:
{
  "cities": [
    {
      "code": "3106200",
      "name": "Belo Horizonte",
      "population": 2521564,
      "area": 331.401,
      "gdp": 95600000000,
      "gdp_per_capita": 37915.23
    }
  ]
}
```

#### **DataSUS - Dados de Saúde**

```javascript
GET /api/v1/federal/datasus/establishments?city=3106200&type=hospital

Response:
{
  "establishments": [
    {
      "cnes": "2001578",
      "name": "Hospital das Clínicas UFMG",
      "type": "Hospital Geral",
      "beds": 450,
      "sus_enabled": true,
      "services": ["emergency", "icu", "surgery"]
    }
  ]
}
```

#### **INEP - Dados Educacionais**

```javascript
GET /api/v1/federal/inep/schools?city=3106200&type=public

Response:
{
  "schools": [
    {
      "code": "31001234",
      "name": "Escola Estadual Central",
      "type": "public",
      "students": 1200,
      "teachers": 65,
      "ideb_score": 6.5,
      "infrastructure": {
        "computer_lab": true,
        "library": true,
        "sports_court": true
      }
    }
  ]
}
```

## 🎨 Dashboard - Dados para Visualização

### **Métricas Gerais**

```javascript
GET /api/v1/dashboard/metrics

Response:
{
  "overview": {
    "total_contracts": 15432,
    "total_value": 4500000000.00,
    "suspicious_contracts": 423,
    "suspicious_value": 125000000.00,
    "investigations_completed": 89,
    "anomalies_detected": 1234
  },
  "by_category": {
    "health": {
      "contracts": 3421,
      "value": 1200000000.00,
      "anomalies": 234
    },
    "education": {
      "contracts": 2145,
      "value": 800000000.00,
      "anomalies": 123
    },
    "infrastructure": {
      "contracts": 1876,
      "value": 2000000000.00,
      "anomalies": 345
    }
  },
  "trends": {
    "monthly": [
      {"month": "2024-01", "value": 350000000, "anomalies": 23},
      {"month": "2024-02", "value": 380000000, "anomalies": 34},
      // ...
    ]
  }
}
```

### **Top Fornecedores**

```javascript
GET /api/v1/dashboard/top-suppliers?limit=10

Response:
{
  "suppliers": [
    {
      "cnpj": "12.345.678/0001-00",
      "name": "Empresa Alpha Ltda",
      "total_contracts": 45,
      "total_value": 125000000.00,
      "risk_score": 0.85,
      "categories": ["health", "technology"],
      "red_flags": ["concentration", "price_above_average"]
    }
  ]
}
```

### **Mapa de Calor - Anomalias por Região**

```javascript
GET /api/v1/dashboard/heatmap?type=anomalies

Response:
{
  "regions": [
    {
      "state": "MG",
      "city": "Belo Horizonte",
      "lat": -19.9167,
      "lng": -43.9345,
      "intensity": 0.75,
      "anomaly_count": 234,
      "total_value": 45000000
    }
  ]
}
```

## 📊 Relatórios e Exportação

### **Gerar Relatório**

```javascript
POST /api/v1/reports/generate
{
  "type": "investigation_summary",
  "format": "pdf",
  "investigation_id": "INV2024-001",
  "include": ["charts", "tables", "recommendations"]
}

Response:
{
  "report_id": "RPT2024-001",
  "status": "processing",
  "estimated_time": 30
}

// Download quando pronto
GET /api/v1/reports/RPT2024-001/download
// Returns: Binary PDF file
```

### **Exportar Dados**

```javascript
POST /api/v1/export/
{
  "data_type": "contracts",
  "format": "xlsx",
  "filters": {
    "year": 2024,
    "min_value": 100000
  }
}

Response:
{
  "export_id": "EXP2024-001",
  "download_url": "/api/v1/export/EXP2024-001/download"
}
```

## 🔐 Autenticação (Opcional)

Por enquanto o sistema está aberto para desenvolvimento. Para produção:

```javascript
// Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "usr_001",
    "email": "user@example.com",
    "name": "João Silva",
    "role": "analyst"
  }
}

// Usar token nos headers
headers: {
  'Authorization': `Bearer ${access_token}`
}
```

## ⚡ WebSocket (Tempo Real)

Para atualizações em tempo real:

```javascript
const ws = new WebSocket('wss://cidadao-api-production.up.railway.app/ws')

ws.onopen = () => {
  // Subscrever a eventos
  ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['investigations', 'anomalies', 'alerts']
  }))
}

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)

  switch(data.type) {
    case 'investigation_update':
      // Atualizar progresso da investigação
      updateInvestigationProgress(data.payload)
      break

    case 'anomaly_detected':
      // Mostrar alerta de nova anomalia
      showAnomalyAlert(data.payload)
      break

    case 'system_alert':
      // Notificação do sistema
      showSystemNotification(data.payload)
      break
  }
}
```

## 📈 Exemplos Práticos de Uso

### **Exemplo 1: Dashboard Inicial**

```javascript
async function loadDashboard() {
  // 1. Carregar métricas gerais
  const metrics = await fetch(`${API_URL}/dashboard/metrics`)
    .then(r => r.json())

  // 2. Carregar top fornecedores suspeitos
  const suppliers = await fetch(`${API_URL}/dashboard/top-suppliers?limit=5`)
    .then(r => r.json())

  // 3. Carregar investigações recentes
  const investigations = await fetch(`${API_URL}/investigations?limit=5&status=completed`)
    .then(r => r.json())

  // 4. Atualizar UI
  updateMetricsCards(metrics.overview)
  renderSuppliersList(suppliers.suppliers)
  renderRecentInvestigations(investigations.items)
}
```

### **Exemplo 2: Investigação Completa**

```javascript
async function runInvestigation(query) {
  // 1. Criar investigação
  const investigation = await fetch(`${API_URL}/investigations/`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      title: query,
      agents: ['zumbi', 'anita', 'tiradentes']
    })
  }).then(r => r.json())

  // 2. Monitorar progresso via SSE
  const eventSource = new EventSource(
    `${API_URL}/investigations/${investigation.investigation_id}/stream`
  )

  eventSource.onmessage = (event) => {
    const progress = JSON.parse(event.data)
    updateProgressBar(progress.percentage)

    if (progress.status === 'completed') {
      displayResults(progress.findings)
      eventSource.close()
    }
  }
}
```

### **Exemplo 3: Chat Interativo**

```javascript
class ChatInterface {
  constructor() {
    this.sessionId = generateUUID()
    this.eventSource = null
  }

  async sendMessage(message) {
    // Mostrar mensagem do usuário
    this.addMessage('user', message)

    // Iniciar streaming
    this.eventSource = new EventSource(`${API_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({
        message,
        session_id: this.sessionId
      })
    })

    let assistantMessage = ''

    this.eventSource.addEventListener('chunk', (e) => {
      const chunk = JSON.parse(e.data)
      assistantMessage += chunk.content
      this.updateAssistantMessage(assistantMessage)
    })

    this.eventSource.addEventListener('complete', (e) => {
      const result = JSON.parse(e.data)
      this.finalizeAssistantMessage(result)
      this.eventSource.close()
    })
  }
}
```

## 🛠️ Tratamento de Erros

```javascript
async function apiCall(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    })

    if (!response.ok) {
      const error = await response.json()

      switch(response.status) {
        case 400:
          throw new ValidationError(error.detail)
        case 401:
          throw new AuthenticationError('Login required')
        case 403:
          throw new AuthorizationError('Access denied')
        case 404:
          throw new NotFoundError(error.detail)
        case 429:
          throw new RateLimitError('Too many requests')
        case 500:
          throw new ServerError('Internal server error')
        default:
          throw new ApiError(error.detail || 'Unknown error')
      }
    }

    return await response.json()

  } catch (error) {
    console.error('API Error:', error)
    // Mostrar notificação ao usuário
    showErrorNotification(error.message)
    throw error
  }
}
```

## 🎯 Melhores Práticas

### 1. **Cache de Dados**

```javascript
class DataCache {
  constructor(ttl = 5 * 60 * 1000) { // 5 minutos
    this.cache = new Map()
    this.ttl = ttl
  }

  async get(key, fetcher) {
    const cached = this.cache.get(key)

    if (cached && Date.now() - cached.timestamp < this.ttl) {
      return cached.data
    }

    const data = await fetcher()
    this.cache.set(key, { data, timestamp: Date.now() })
    return data
  }
}

const cache = new DataCache()

// Usar cache
const contracts = await cache.get(
  'contracts_2024',
  () => fetch(`${API_URL}/transparency/contracts?year=2024`).then(r => r.json())
)
```

### 2. **Debounce para Pesquisas**

```javascript
function debounce(func, delay) {
  let timeoutId
  return function(...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func.apply(this, args), delay)
  }
}

const searchContracts = debounce(async (query) => {
  const results = await fetch(`${API_URL}/search?q=${query}`).then(r => r.json())
  displaySearchResults(results)
}, 300)
```

### 3. **Loading States**

```javascript
class ApiLoader {
  async loadWithState(loader, callback) {
    this.setLoading(true)
    this.clearError()

    try {
      const data = await loader()
      callback(data)
    } catch (error) {
      this.setError(error.message)
    } finally {
      this.setLoading(false)
    }
  }
}
```

## 📱 Responsividade

O backend retorna dados otimizados para mobile quando detectado:

```javascript
// Headers para mobile
headers: {
  'X-Client-Type': 'mobile',
  'X-Screen-Size': 'small'
}

// Response será otimizada (menos dados, paginação menor)
```

## 🔄 Atualizações e Versionamento

```javascript
// Verificar versão da API
GET /api/version

Response:
{
  "version": "1.0.0",
  "minimum_client_version": "1.0.0",
  "features": {
    "streaming": true,
    "websocket": true,
    "export": true
  }
}
```

## 📞 Suporte e Limites

### **Rate Limiting**

- 60 requisições por minuto (geral)
- 10 requisições por minuto (investigações)
- 100 requisições por minuto (leitura)

Headers de resposta:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

### **Limites de Dados**

- Máximo 1000 itens por página
- Máximo 10MB por requisição
- Timeout: 30 segundos (geral), 5 minutos (investigações)

## 🚀 Quick Start - Código Inicial

```html
<!DOCTYPE html>
<html>
<head>
    <title>Cidadão.AI</title>
</head>
<body>
    <div id="app"></div>

    <script>
        // Configuração
        const API = {
            BASE_URL: 'https://cidadao-api-production.up.railway.app',
            VERSION: '/api/v1'
        }

        // Classe principal
        class CidadaoAI {
            constructor() {
                this.apiUrl = `${API.BASE_URL}${API.VERSION}`
            }

            async getAgents() {
                const response = await fetch(`${this.apiUrl}/agents/`)
                return response.json()
            }

            async analyzeWithAgent(agentId, query) {
                const response = await fetch(`${this.apiUrl}/agents/${agentId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ query, context: {} })
                })
                return response.json()
            }

            async getContracts(filters = {}) {
                const params = new URLSearchParams(filters)
                const response = await fetch(`${this.apiUrl}/transparency/contracts?${params}`)
                return response.json()
            }
        }

        // Inicializar
        const cidadao = new CidadaoAI()

        // Exemplo de uso
        async function init() {
            // 1. Listar agentes
            const agents = await cidadao.getAgents()
            console.log('Agentes disponíveis:', agents)

            // 2. Analisar com Zumbi
            const analysis = await cidadao.analyzeWithAgent('zumbi', 'Encontre anomalias em contratos')
            console.log('Análise:', analysis)

            // 3. Buscar contratos
            const contracts = await cidadao.getContracts({ year: 2024, limit: 10 })
            console.log('Contratos:', contracts)
        }

        init()
    </script>
</body>
</html>
```

---

## 📊 Resumo dos Recursos

### **O que o Frontend receberá desta API:**

✅ **16 Agentes de IA** com personalidades históricas brasileiras
✅ **Dados completos** do Portal da Transparência (contratos, licitações, servidores)
✅ **APIs Federais** integradas (IBGE, DataSUS, INEP, PNCP)
✅ **Investigações automatizadas** com múltiplos agentes
✅ **Chat com streaming** (SSE) para respostas em tempo real
✅ **Dashboard** com métricas, gráficos e mapas de calor
✅ **Relatórios** em PDF/Excel com gráficos e análises
✅ **WebSocket** para notificações em tempo real
✅ **Sistema de busca** com filtros avançados
✅ **Exportação de dados** em múltiplos formatos

### **O Frontend NÃO precisa:**

❌ Banco de dados próprio
❌ Processamento de dados complexos
❌ Integração direta com APIs governamentais
❌ Lógica de IA ou análise
❌ Geração de relatórios

---

**🎯 IMPORTANTE**: Este backend é a **ÚNICA fonte de dados** para o frontend. Todos os dados mostrados na interface virão exclusivamente desta API.

**📧 Contato para dúvidas**: [documentação completa em /docs](https://cidadao-api-production.up.railway.app/docs)

---

*Última atualização: 21/11/2025 - Sistema 100% operacional com 16 agentes funcionais*
