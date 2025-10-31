# GUIA TÉCNICO DE INTEGRAÇÃO FRONTEND-BACKEND
# CIDADÃO.AI - Plataforma de Transparência Pública

**Versão**: 1.0
**Data**: 2025-10-22
**Autor**: Anderson H. Silva
**Tipo**: Documentação Técnica Completa
**Público**: Desenvolvedores Frontend

---

## ÍNDICE

1. [Visão Geral da API](#1-visão-geral-da-api)
2. [Autenticação e Segurança](#2-autenticação-e-segurança)
3. [Sistema de Chat](#3-sistema-de-chat)
4. [Sistema de Agentes](#4-sistema-de-agentes)
5. [Sistema de Investigações](#5-sistema-de-investigações)
6. [APIs Federais e Dados Governamentais](#6-apis-federais-e-dados-governamentais)
7. [Exportação de Dados](#7-exportação-de-dados)
8. [Visualização e Rede](#8-visualização-e-rede)
9. [Streaming e Tempo Real](#9-streaming-e-tempo-real)
10. [Estruturas de Dados](#10-estruturas-de-dados)
11. [Exemplos de Integração](#11-exemplos-de-integração)
12. [Tratamento de Erros](#12-tratamento-de-erros)
13. [Performance e Otimização](#13-performance-e-otimização)
14. [Referência Rápida](#14-referência-rápida)

---

## 1. VISÃO GERAL DA API

### 1.1 Informações Básicas

```
Base URL (Produção): https://cidadao-api-production.up.railway.app
Base URL (Local):    http://localhost:8000

Documentação:  /docs (Swagger UI)
OpenAPI:       /openapi.json
ReDoc:         /redoc

Total de Endpoints: 262
Schemas de Dados:   124
```

### 1.2 Categorias de Endpoints

| Categoria | Endpoints | Descrição |
|-----------|-----------|-----------|
| **Chat** | 10 | Sistema de conversação com agentes |
| **Agents** | 25 | Invocação direta de agentes especializados |
| **Investigations** | 16 | Criação e gerenciamento de investigações |
| **Federal APIs** | 7 | Dados de APIs governamentais (IBGE, DataSUS, etc) |
| **Export** | 8 | Exportação em múltiplos formatos |
| **Network** | 8 | Análise de rede e grafos |
| **Transparency** | 6 | Portal da Transparência |
| **Authentication** | 17 | Login, OAuth, JWT |
| **Metrics** | 5 | Métricas e analytics |
| **Admin** | 35 | Administração e configuração |
| **Health** | 12 | Status e saúde do sistema |
| **Other** | 113 | Utilitários diversos |

### 1.3 Formato de Resposta Padrão

Todas as respostas seguem este padrão:

```typescript
interface APIResponse<T> {
  // Sucesso
  status?: "success" | "error";
  data?: T;
  message?: string;

  // Paginação (quando aplicável)
  total?: number;
  page?: number;
  limit?: number;

  // Erro
  error?: {
    code: string;
    message: string;
    details?: any;
  };

  // Metadata
  metadata?: {
    timestamp: string;
    request_id: string;
    [key: string]: any;
  };
}
```

---

## 2. AUTENTICAÇÃO E SEGURANÇA

### 2.1 Métodos de Autenticação Disponíveis

#### A. JWT Token (Recomendado)
```typescript
// Login
POST /api/v1/auth/login
Request: {
  "username": "string",
  "password": "string"
}
Response: {
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800  // 30 minutos
}

// Usar token
Headers: {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### B. API Key
```typescript
// Endpoints que aceitam API Key
Headers: {
  "X-API-Key": "your-api-key-here"
}
```

#### C. OAuth2 (Social Login)
```typescript
// Google OAuth
GET /api/v1/oauth/google/authorize
// Redireciona para Google

// Callback
GET /api/v1/oauth/google/callback?code=...
Response: {
  "access_token": "...",
  "user": { ... }
}
```

### 2.2 Refresh Token

```typescript
POST /api/v1/auth/refresh
Request: {
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
Response: {
  "access_token": "new_access_token...",
  "expires_in": 1800
}
```

### 2.3 Endpoints Públicos (Sem Auth)

Estes endpoints **NÃO** requerem autenticação:

- `GET /` - Root
- `GET /health/` - Health check
- `GET /docs` - Documentação
- `GET /openapi.json` - Schema
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Registro
- `GET /api/v1/chat/agents` - Lista de agentes
- `GET /api/v1/federal/ibge/*` - Dados IBGE

---

## 3. SISTEMA DE CHAT

### 3.1 Enviar Mensagem

#### Endpoint Principal
```typescript
POST /api/v1/chat/message

Request: {
  "message": string;           // Mensagem do usuário (1-1000 chars)
  "session_id"?: string;       // ID da sessão (opcional, gera automático)
  "context"?: {                // Contexto adicional (opcional)
    "user_location"?: string;
    "filters"?: object;
    [key: string]: any;
  }
}

Response: {
  "session_id": string;              // ID da sessão
  "message_id": string;              // ID da mensagem
  "agent_id": string;                // Agente que respondeu
  "agent_name": string;              // Nome do agente
  "message": string;                 // Resposta do agente
  "confidence": number;              // Confiança (0-1)
  "suggested_actions"?: string[];    // Ações sugeridas
  "follow_up_questions"?: string[];  // Perguntas de follow-up
  "requires_input"?: {               // Input necessário
    [field: string]: string;
  };
  "metadata": {
    "intent": string;                // Intenção detectada
    "data_source"?: string;          // Fonte de dados usada
    "processing_time_ms": number;    // Tempo de processamento
    [key: string]: any;
  }
}
```

#### Exemplo de Uso

```typescript
// Frontend TypeScript
async function sendChatMessage(message: string, sessionId?: string) {
  const response = await fetch('https://cidadao-api-production.up.railway.app/api/v1/chat/message', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  const data = await response.json();
  return data;
}

// Uso
const result = await sendChatMessage(
  "Quais são os maiores contratos do Ministério da Saúde em 2024?"
);

console.log(result.message);  // Resposta do agente
console.log(result.agent_name);  // "Zumbi dos Palmares"
console.log(result.suggested_actions);  // ["Ver detalhes", "Exportar dados"]
```

### 3.2 Listar Agentes Disponíveis para Chat

```typescript
GET /api/v1/chat/agents

Response: Array<{
  "id": string;           // ID do agente (ex: "zumbi", "anita")
  "name": string;         // Nome completo
  "avatar": string;       // Emoji avatar
  "role": string;         // Função principal
  "description": string;  // Descrição
  "status": "active" | "inactive";
}>

// Exemplo de resposta
[
  {
    "id": "abaporu",
    "name": "Abaporu",
    "avatar": "🎨",
    "role": "Orquestrador Master",
    "description": "Coordena investigações complexas",
    "status": "active"
  },
  {
    "id": "zumbi",
    "name": "Zumbi dos Palmares",
    "avatar": "🔍",
    "role": "Investigador",
    "description": "Detecta anomalias e irregularidades",
    "status": "active"
  },
  // ... mais 4 agentes
]
```

### 3.3 Streaming de Chat (Server-Sent Events)

```typescript
GET /api/v1/chat/stream/{session_id}

// Frontend: EventSource API
const eventSource = new EventSource(
  'https://cidadao-api-production.up.railway.app/api/v1/chat/stream/session-123'
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'message_chunk') {
    // Chunk da mensagem do agente
    appendToChat(data.content);
  } else if (data.type === 'agent_thinking') {
    // Agente está processando
    showThinkingIndicator(data.agent_name);
  } else if (data.type === 'data_fetched') {
    // Dados foram coletados
    showDataPreview(data.summary);
  } else if (data.type === 'complete') {
    // Resposta completa
    hideThinkingIndicator();
  }
};

eventSource.onerror = () => {
  eventSource.close();
  showError('Conexão perdida');
};
```

### 3.4 Histórico de Chat

```typescript
GET /api/v1/chat/history/{session_id}?limit=50&offset=0

Response: {
  "session_id": string;
  "messages": Array<{
    "message_id": string;
    "role": "user" | "agent";
    "content": string;
    "agent_id"?: string;
    "timestamp": string;  // ISO 8601
    "metadata": object;
  }>;
  "total": number;
  "has_more": boolean;
}
```

---

## 4. SISTEMA DE AGENTES

### 4.1 Listar Todos os Agentes

```typescript
GET /api/v1/agents/

Response: {
  "message": "Cidadão.AI Agent System",
  "version": "2.0.0",
  "agents": Array<{
    "name": string;
    "endpoint": string;
    "description": string;
  }>
}

// Exemplo
{
  "agents": [
    {
      "name": "Zumbi dos Palmares",
      "endpoint": "/api/v1/agents/zumbi",
      "description": "Anomaly detection and investigation specialist"
    },
    // ... 15 agentes
  ]
}
```

### 4.2 Status Detalhado dos Agentes

```typescript
GET /api/v1/agents/status

Response: {
  "agents": {
    "zumbi_dos_palmares": {
      "name": string;
      "role": string;
      "status": "active" | "inactive" | "maintenance";
      "capabilities": string[];
    },
    // ... demais agentes
  }
}

// Exemplo completo
{
  "agents": {
    "zumbi_dos_palmares": {
      "name": "Zumbi dos Palmares",
      "role": "Anomaly Detection Specialist",
      "status": "active",
      "capabilities": [
        "Price anomaly detection",
        "Vendor concentration analysis",
        "Temporal pattern recognition",
        "Contract duplication detection",
        "Payment irregularity identification"
      ]
    },
    "anita_garibaldi": {
      "name": "Anita Garibaldi",
      "role": "Pattern Analysis Specialist",
      "status": "active",
      "capabilities": [
        "Spending trend analysis",
        "Organizational behavior mapping",
        "Vendor relationship analysis",
        "Seasonal pattern detection",
        "Efficiency metrics calculation"
      ]
    }
    // ... mais agentes
  }
}
```

### 4.3 Invocar Agente Específico

#### A. Zumbi dos Palmares (Anomaly Detection)

```typescript
POST /api/v1/agents/zumbi

Request: {
  "query": string;           // Consulta ou foco da análise
  "context": {               // Contexto adicional
    "data_source"?: "contracts" | "expenses" | "biddings";
    "time_period"?: {
      "start": string;  // ISO date
      "end": string;    // ISO date
    };
    "agency"?: string;
    "value_threshold"?: number;
  };
  "options": {               // Opções de detecção
    "anomaly_types"?: ["price", "vendor", "temporal", "payment"];
    "sensitivity"?: "low" | "medium" | "high";
    "include_explanations"?: boolean;
  }
}

Response: {
  "agent": "zumbi_dos_palmares",
  "result": {
    "anomalies_found": number;
    "anomalies": Array<{
      "type": string;
      "severity": "low" | "medium" | "high" | "critical";
      "description": string;
      "affected_entities": string[];
      "confidence": number;
      "evidence": object;
      "recommendation": string;
    }>;
    "summary": {
      "total_records_analyzed": number;
      "anomaly_rate": number;
      "critical_findings": number;
    };
  };
  "metadata": {
    "processing_time_ms": number;
    "data_source": string;
    "analysis_date": string;
  };
  "success": boolean;
  "message"?: string;
}
```

#### B. Anita Garibaldi (Pattern Analysis)

```typescript
POST /api/v1/agents/anita

Request: {
  "query": string;
  "context": {
    "analysis_type"?: "trend" | "correlation" | "clustering" | "forecast";
    "data_source"?: string;
    "time_granularity"?: "daily" | "weekly" | "monthly" | "yearly";
  };
  "options": {
    "include_visualizations"?: boolean;
    "statistical_tests"?: boolean;
  }
}

Response: {
  "agent": "anita_garibaldi",
  "result": {
    "patterns_found": number;
    "patterns": Array<{
      "type": string;
      "description": string;
      "significance": number;
      "trend_direction"?: "increasing" | "decreasing" | "stable";
      "correlation_coefficient"?: number;
      "visualization_data"?: object;
    }>;
    "insights": string[];
    "statistical_summary": object;
  };
  "success": boolean;
}
```

#### C. Tiradentes (Report Generation)

```typescript
POST /api/v1/agents/tiradentes

Request: {
  "query": string;
  "context": {
    "report_type"?: "executive" | "detailed" | "technical";
    "format"?: "markdown" | "html" | "json";
    "sections"?: string[];  // Seções a incluir
    "investigation_id"?: string;  // Vincular a investigação
  };
  "options": {
    "include_charts"?: boolean;
    "include_raw_data"?: boolean;
    "language"?: "pt-BR" | "en-US";
  }
}

Response: {
  "agent": "tiradentes",
  "result": {
    "report_id": string;
    "title": string;
    "content": string;  // Markdown/HTML
    "sections": Array<{
      "title": string;
      "content": string;
      "charts"?: object[];
    }>;
    "summary": string;
    "recommendations": string[];
    "export_urls"?: {
      "pdf"?: string;
      "html"?: string;
      "docx"?: string;
    };
  };
  "success": boolean;
}
```

### 4.4 Agentes Disponíveis (Resumo)

| Agente | Endpoint | Especialização |
|--------|----------|----------------|
| **Zumbi dos Palmares** | `/api/v1/agents/zumbi` | Detecção de anomalias |
| **Anita Garibaldi** | `/api/v1/agents/anita` | Análise de padrões |
| **Tiradentes** | `/api/v1/agents/tiradentes` | Geração de relatórios |
| **José Bonifácio** | `/api/v1/agents/bonifacio` | Compliance legal |
| **Maria Quitéria** | `/api/v1/agents/maria-quiteria` | Auditoria de segurança |
| **Machado de Assis** | `/api/v1/agents/machado` | Análise textual |
| **Dandara** | `/api/v1/agents/dandara` | Equidade social |
| **Abaporu** | `/api/v1/agents/abaporu` | Orquestração |
| **Ayrton Senna** | `/api/v1/agents/ayrton-senna` | Roteamento inteligente |
| **Lampião** | `/api/v1/agents/lampiao` | Análise regional |
| **Oscar Niemeyer** | `/api/v1/agents/oscar` | Visualização |
| **Oxóssi** | `/api/v1/agents/oxossi` | Detecção de fraude |
| **Nanã** | `/api/v1/agents/nana` | Sistema de memória |
| **Drummond** | `/api/v1/agents/drummond` | Comunicação |
| **Céuci** | `/api/v1/agents/ceuci` | ML/Preditivo |
| **Obaluaiê** | `/api/v1/agents/obaluaie` | Detecção de corrupção |

---

## 5. SISTEMA DE INVESTIGAÇÕES

### 5.1 Criar Nova Investigação

```typescript
POST /api/v1/investigations/start

Request: {
  "query": string;                    // Foco da investigação
  "data_source": "contracts" | "expenses" | "agreements" | "biddings" | "servants";
  "filters": {                        // Filtros opcionais
    "agency"?: string;
    "date_range"?: {
      "start": string;
      "end": string;
    };
    "value_range"?: {
      "min": number;
      "max": number;
    };
    "location"?: {
      "state"?: string;
      "city"?: string;
    };
    [key: string]: any;
  };
  "anomaly_types": string[];          // ["price", "vendor", "temporal", "payment"]
  "include_explanations": boolean;    // Default: true
  "stream_results": boolean;          // Default: false
}

Response: {
  "investigation_id": string;         // UUID da investigação
  "status": "pending" | "processing" | "completed" | "failed";
  "query": string;
  "created_at": string;               // ISO 8601
  "estimated_completion_time"?: number;  // Segundos
  "stream_url"?: string;              // Se stream_results = true
}

// Exemplo
{
  "investigation_id": "inv_123abc456def",
  "status": "processing",
  "query": "Contratos de TI acima de R$ 1 milhão em 2024",
  "created_at": "2025-10-22T14:30:00Z",
  "estimated_completion_time": 45,
  "stream_url": "/api/v1/investigations/stream/inv_123abc456def"
}
```

### 5.2 Listar Investigações

```typescript
GET /api/v1/investigations/?status=all&limit=20&offset=0

Query Parameters:
  - status: "all" | "pending" | "processing" | "completed" | "failed"
  - limit: number (default: 20, max: 100)
  - offset: number (default: 0)
  - sort_by: "created_at" | "updated_at" | "status"
  - order: "asc" | "desc"

Response: Array<{
  "investigation_id": string;
  "query": string;
  "status": string;
  "data_source": string;
  "created_at": string;
  "updated_at": string;
  "anomalies_found"?: number;
  "progress"?: number;  // 0-100
}>

// Exemplo
[
  {
    "investigation_id": "inv_123abc",
    "query": "Contratos de TI acima de R$ 1 milhão",
    "status": "completed",
    "data_source": "contracts",
    "created_at": "2025-10-22T14:30:00Z",
    "updated_at": "2025-10-22T14:31:23Z",
    "anomalies_found": 12,
    "progress": 100
  }
]
```

### 5.3 Obter Status da Investigação

```typescript
GET /api/v1/investigations/{investigation_id}/status

Response: {
  "investigation_id": string;
  "status": "pending" | "processing" | "completed" | "failed";
  "progress": number;              // 0-100
  "current_step"?: string;
  "steps_completed": number;
  "total_steps": number;
  "started_at": string;
  "updated_at": string;
  "estimated_time_remaining"?: number;  // Segundos
  "error"?: {
    "message": string;
    "code": string;
  };
}
```

### 5.4 Obter Resultados da Investigação

```typescript
GET /api/v1/investigations/{investigation_id}/results

Response: {
  "investigation_id": string;
  "query": string;
  "status": "completed";
  "results": {
    "summary": {
      "total_records_analyzed": number;
      "anomalies_found": number;
      "critical_findings": number;
      "data_quality_score": number;  // 0-1
    };
    "anomalies": Array<{
      "id": string;
      "type": "price" | "vendor" | "temporal" | "payment" | "duplicate" | "pattern";
      "severity": "low" | "medium" | "high" | "critical";
      "title": string;
      "description": string;
      "affected_entities": Array<{
        "type": "contract" | "vendor" | "agency";
        "id": string;
        "name": string;
      }>;
      "evidence": {
        "statistical_analysis"?: object;
        "comparison_data"?: object;
        "supporting_documents"?: string[];
      };
      "confidence": number;  // 0-1
      "financial_impact"?: {
        "estimated_loss": number;
        "currency": "BRL";
      };
      "recommendation": string;
      "priority": number;  // 1-5
    }>;
    "insights": string[];
    "recommendations": string[];
    "visualizations"?: Array<{
      "type": "chart" | "graph" | "heatmap";
      "title": string;
      "data": object;
      "config": object;
    }>;
  };
  "metadata": {
    "processing_time_ms": number;
    "agents_involved": string[];
    "data_sources": string[];
    "completion_date": string;
  };
}
```

### 5.5 Streaming de Investigação (SSE)

```typescript
GET /api/v1/investigations/stream/{investigation_id}

// Frontend: EventSource
const eventSource = new EventSource(
  `https://cidadao-api-production.up.railway.app/api/v1/investigations/stream/inv_123`
);

eventSource.addEventListener('progress', (event) => {
  const data = JSON.parse(event.data);
  // { "progress": 45, "current_step": "Analyzing contracts" }
  updateProgressBar(data.progress);
  showCurrentStep(data.current_step);
});

eventSource.addEventListener('anomaly_found', (event) => {
  const anomaly = JSON.parse(event.data);
  // { "type": "price", "severity": "high", "description": "..." }
  addAnomalyToList(anomaly);
});

eventSource.addEventListener('complete', (event) => {
  const results = JSON.parse(event.data);
  eventSource.close();
  showFinalResults(results);
});

eventSource.addEventListener('error', (event) => {
  const error = JSON.parse(event.data);
  eventSource.close();
  showError(error.message);
});
```

### 5.6 Deletar Investigação

```typescript
DELETE /api/v1/investigations/{investigation_id}

Response: {
  "message": "Investigation deleted successfully",
  "investigation_id": string;
}
```

### 5.7 Investigação Pública (Sem Auth)

```typescript
POST /api/v1/investigations/public/create

Request: {
  "query": string;
  "email": string;  // Para envio de resultados
}

Response: {
  "investigation_id": string;
  "status_url": string;
  "message": "Investigation created. Check your email for results."
}

// Verificar status
GET /api/v1/investigations/public/status/{investigation_id}
```

---

## 6. APIS FEDERAIS E DADOS GOVERNAMENTAIS

### 6.1 IBGE (Instituto Brasileiro de Geografia e Estatística)

#### Estados
```typescript
GET /api/v1/federal/ibge/states

Response: {
  "success": true,
  "total": 27,
  "data": Array<{
    "id": string;
    "nome": string;
    "regiao": {
      "id": number;
      "sigla": string;
      "nome": string;
    };
  }>
}

// Exemplo
{
  "success": true,
  "total": 27,
  "data": [
    {
      "id": "33",
      "nome": "Rio de Janeiro",
      "regiao": {
        "id": 3,
        "sigla": "SE",
        "nome": "Sudeste"
      }
    }
  ]
}
```

#### Municípios
```typescript
GET /api/v1/federal/ibge/municipalities?state_code=33

Query Parameters:
  - state_code: string (UF code, ex: "33" para RJ)

Response: {
  "success": true,
  "total": number,
  "data": Array<{
    "id": string;
    "nome": string;
    "microrregiao": object;
    "mesorregiao": object;
  }>
}
```

#### Distritos
```typescript
GET /api/v1/federal/ibge/districts?municipality_code=3304557

Response: {
  "success": true,
  "data": Array<{
    "id": string;
    "nome": string;
    "municipio": object;
  }>
}
```

### 6.2 DataSUS (Sistema Único de Saúde)

```typescript
GET /api/v1/federal/datasus/establishments?state=RJ&type=hospital

Query Parameters:
  - state: string (UF)
  - type: "hospital" | "clinic" | "ubs" | "all"
  - specialty?: string
  - limit?: number

Response: {
  "success": true,
  "data": Array<{
    "cnes": string;
    "name": string;
    "type": string;
    "address": object;
    "services": string[];
  }>
}
```

### 6.3 INEP (Educação)

```typescript
GET /api/v1/federal/inep/schools?state=RJ&municipality=Rio de Janeiro

Response: {
  "success": true,
  "data": Array<{
    "school_code": string;
    "name": string;
    "type": string;
    "address": object;
    "statistics": object;
  }>
}
```

### 6.4 PNCP (Portal Nacional de Contratações Públicas)

```typescript
GET /api/v1/federal/pncp/contracts?agency_code=26000&year=2024

Query Parameters:
  - agency_code: string
  - year: number
  - status?: "active" | "completed" | "canceled"
  - min_value?: number
  - max_value?: number

Response: {
  "success": true,
  "total": number,
  "data": Array<{
    "contract_id": string;
    "title": string;
    "agency": string;
    "vendor": string;
    "value": number;
    "date": string;
    "status": string;
  }>
}
```

### 6.5 Portal da Transparência

```typescript
GET /api/v1/transparency/contracts?codigoOrgao=26000&ano=2024

Query Parameters:
  - codigoOrgao: string (required)
  - ano: number
  - mes?: number
  - pagina?: number

Response: {
  "data": Array<{
    "numero": string;
    "objeto": string;
    "fornecedor": object;
    "valor": number;
    "dataAssinatura": string;
  }>;
  "total": number;
}

// Nota: Apenas 22% dos endpoints funcionam
// Use Federal APIs como alternativa
```

---

## 7. EXPORTAÇÃO DE DADOS

### 7.1 Exportar Investigação

```typescript
POST /api/v1/export/investigations/{investigation_id}/download

Request: {
  "format": "json" | "csv" | "excel" | "pdf";
  "sections"?: string[];  // Seções a incluir
  "include_charts"?: boolean;
  "language"?: "pt-BR" | "en-US";
}

Response: {
  "download_url": string;
  "expires_at": string;  // ISO 8601
  "file_size": number;   // bytes
  "format": string;
}

// Ou resposta direta (file download)
// Content-Type: application/json | text/csv | application/vnd.ms-excel | application/pdf
// Content-Disposition: attachment; filename="investigation_123.xlsx"
```

### 7.2 Formatos Disponíveis

#### JSON
```json
{
  "investigation": {
    "id": "inv_123",
    "query": "...",
    "results": { ... }
  }
}
```

#### CSV
```csv
Anomaly Type,Severity,Description,Confidence,Financial Impact
price,high,Preço 300% acima da média,0.95,R$ 500000
vendor,medium,Concentração em único fornecedor,0.87,R$ 200000
```

#### Excel (.xlsx)
- Múltiplas planilhas
- Formatação condicional
- Gráficos embarcados
- Filtros automáticos

#### PDF
- Report formatado
- Gráficos e visualizações
- Sumário executivo
- Anexos com dados brutos

---

## 8. VISUALIZAÇÃO E REDE

### 8.1 Análise de Rede de Entidades

```typescript
GET /api/v1/network/entities/{entity_id}/connections?depth=2

Query Parameters:
  - depth: number (1-3, níveis de conexões)
  - entity_type?: "vendor" | "agency" | "contract"
  - min_strength?: number (0-1)

Response: {
  "entity": {
    "id": string;
    "type": string;
    "name": string;
    "metadata": object;
  };
  "connections": Array<{
    "target_entity": {
      "id": string;
      "type": string;
      "name": string;
    };
    "relationship_type": string;
    "strength": number;  // 0-1
    "evidence": object[];
  }>;
  "graph_data": {
    "nodes": Array<{ id, label, type, ... }>;
    "edges": Array<{ source, target, weight, ... }>;
  };
}
```

### 8.2 Visualizações de Dados

```typescript
GET /api/v1/visualization/generate

Request: {
  "type": "bar" | "line" | "pie" | "scatter" | "heatmap" | "network";
  "data_source": string;
  "config": {
    "title": string;
    "x_axis"?: string;
    "y_axis"?: string;
    "group_by"?: string;
    "aggregation"?: "sum" | "avg" | "count";
    "colors"?: string[];
  };
}

Response: {
  "visualization_id": string;
  "type": string;
  "data": object;  // Plotly/Chart.js compatible
  "config": object;
  "embed_url"?: string;
  "image_url"?: string;
}
```

---

## 9. STREAMING E TEMPO REAL

### 9.1 Server-Sent Events (SSE)

Endpoints que suportam SSE:

```typescript
// Investigação
GET /api/v1/investigations/stream/{investigation_id}

// Chat
GET /api/v1/chat/stream/{session_id}

// Monitoramento em tempo real
GET /api/v1/monitoring/stream
```

### 9.2 WebSocket

```typescript
// Conectar
const ws = new WebSocket('wss://cidadao-api-production.up.railway.app/api/v1/ws');

ws.onopen = () => {
  // Autenticar
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'jwt_token_here'
  }));

  // Subscrever a eventos
  ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['investigations', 'notifications']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case 'investigation_update':
      updateInvestigation(data.payload);
      break;
    case 'notification':
      showNotification(data.payload);
      break;
  }
};
```

---

## 10. ESTRUTURAS DE DADOS

### 10.1 Modelos Principais

#### Investigation
```typescript
interface Investigation {
  investigation_id: string;
  query: string;
  data_source: DataSource;
  status: InvestigationStatus;
  filters: Record<string, any>;
  anomaly_types: AnomalyType[];
  results?: InvestigationResults;
  created_at: string;
  updated_at: string;
  created_by?: string;
  metadata: Record<string, any>;
}

type InvestigationStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "canceled";

type DataSource =
  | "contracts"
  | "expenses"
  | "agreements"
  | "biddings"
  | "servants";

type AnomalyType =
  | "price"
  | "vendor"
  | "temporal"
  | "payment"
  | "duplicate"
  | "pattern";
```

#### Anomaly
```typescript
interface Anomaly {
  id: string;
  type: AnomalyType;
  severity: "low" | "medium" | "high" | "critical";
  title: string;
  description: string;
  affected_entities: Entity[];
  evidence: Evidence;
  confidence: number;  // 0-1
  financial_impact?: FinancialImpact;
  recommendation: string;
  priority: number;  // 1-5
  created_at: string;
}

interface Entity {
  type: "contract" | "vendor" | "agency" | "servant";
  id: string;
  name: string;
  metadata?: Record<string, any>;
}

interface Evidence {
  statistical_analysis?: StatisticalData;
  comparison_data?: ComparisonData;
  supporting_documents?: string[];
  timeline?: TimelineEvent[];
}

interface FinancialImpact {
  estimated_loss: number;
  currency: "BRL";
  calculation_method: string;
  confidence: number;
}
```

#### Agent
```typescript
interface Agent {
  id: string;
  name: string;
  avatar: string;
  role: string;
  description: string;
  status: "active" | "inactive" | "maintenance";
  capabilities: string[];
  endpoint: string;
}
```

#### ChatMessage
```typescript
interface ChatMessage {
  message_id: string;
  session_id: string;
  role: "user" | "agent" | "system";
  content: string;
  agent_id?: string;
  agent_name?: string;
  confidence?: number;
  suggested_actions?: string[];
  follow_up_questions?: string[];
  requires_input?: Record<string, string>;
  metadata: Record<string, any>;
  timestamp: string;
}
```

### 10.2 Enums e Constantes

```typescript
// Severity Levels
enum Severity {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}

// Agent IDs
enum AgentId {
  ZUMBI = "zumbi",
  ANITA = "anita",
  TIRADENTES = "tiradentes",
  BONIFACIO = "bonifacio",
  MARIA_QUITERIA = "maria_quiteria",
  MACHADO = "machado",
  DANDARA = "dandara",
  ABAPORU = "abaporu",
  AYRTON_SENNA = "ayrton_senna",
  LAMPIAO = "lampiao",
  OSCAR = "oscar",
  OXOSSI = "oxossi",
  NANA = "nana",
  DRUMMOND = "drummond",
  CEUCI = "ceuci",
  OBALUAIE = "obaluaie"
}

// Export Formats
enum ExportFormat {
  JSON = "json",
  CSV = "csv",
  EXCEL = "excel",
  PDF = "pdf"
}
```

---

## 11. EXEMPLOS DE INTEGRAÇÃO

### 11.1 React Hook Completo

```typescript
// useCidadaoAI.ts
import { useState, useEffect, useCallback } from 'react';

const API_BASE = 'https://cidadao-api-production.up.railway.app';

interface ChatMessage {
  role: 'user' | 'agent';
  content: string;
  agent_name?: string;
  timestamp: string;
}

export function useCidadaoAI() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);

  // Carregar agentes disponíveis
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/chat/agents`)
      .then(res => res.json())
      .then(data => setAgents(data));
  }, []);

  // Enviar mensagem
  const sendMessage = useCallback(async (message: string) => {
    setIsLoading(true);

    // Adicionar mensagem do usuário
    setMessages(prev => [...prev, {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    }]);

    try {
      const response = await fetch(`${API_BASE}/api/v1/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          session_id: sessionId
        })
      });

      const data = await response.json();

      // Salvar session_id
      if (!sessionId) {
        setSessionId(data.session_id);
      }

      // Adicionar resposta do agente
      setMessages(prev => [...prev, {
        role: 'agent',
        content: data.message,
        agent_name: data.agent_name,
        timestamp: new Date().toISOString()
      }]);

      return data;
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  return {
    messages,
    sendMessage,
    isLoading,
    agents,
    sessionId
  };
}
```

### 11.2 Componente React de Chat

```typescript
// ChatInterface.tsx
import React, { useState } from 'react';
import { useCidadaoAI } from './useCidadaoAI';

export function ChatInterface() {
  const { messages, sendMessage, isLoading, agents } = useCidadaoAI();
  const [input, setInput] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    await sendMessage(input);
    setInput('');
  };

  return (
    <div className="chat-container">
      {/* Lista de agentes */}
      <div className="agents-sidebar">
        <h3>Agentes Disponíveis</h3>
        {agents.map(agent => (
          <div key={agent.id} className="agent-card">
            <span className="agent-avatar">{agent.avatar}</span>
            <div>
              <strong>{agent.name}</strong>
              <p>{agent.description}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Área de mensagens */}
      <div className="messages-area">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.role === 'agent' && (
              <strong>{msg.agent_name}: </strong>
            )}
            <p>{msg.content}</p>
            <span className="timestamp">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </span>
          </div>
        ))}

        {isLoading && (
          <div className="message agent">
            <span className="typing-indicator">...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Digite sua pergunta..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Enviar
        </button>
      </form>
    </div>
  );
}
```

### 11.3 Criar e Monitorar Investigação

```typescript
// useInvestigation.ts
import { useState, useEffect } from 'react';

const API_BASE = 'https://cidadao-api-production.up.railway.app';

export function useInvestigation() {
  const [investigations, setInvestigations] = useState([]);
  const [isCreating, setIsCreating] = useState(false);

  // Criar investigação
  const createInvestigation = async (query: string, filters = {}) => {
    setIsCreating(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/investigations/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          data_source: 'contracts',
          filters,
          anomaly_types: ['price', 'vendor', 'temporal'],
          include_explanations: true,
          stream_results: true
        })
      });

      const data = await response.json();

      // Monitorar via SSE
      if (data.stream_url) {
        monitorInvestigation(data.investigation_id);
      }

      return data;
    } catch (error) {
      console.error('Erro ao criar investigação:', error);
      throw error;
    } finally {
      setIsCreating(false);
    }
  };

  // Monitorar investigação via SSE
  const monitorInvestigation = (investigationId: string) => {
    const eventSource = new EventSource(
      `${API_BASE}/api/v1/investigations/stream/${investigationId}`
    );

    eventSource.addEventListener('progress', (event) => {
      const data = JSON.parse(event.data);
      console.log(`Progresso: ${data.progress}%`);
      // Atualizar UI com progresso
    });

    eventSource.addEventListener('anomaly_found', (event) => {
      const anomaly = JSON.parse(event.data);
      console.log('Anomalia encontrada:', anomaly);
      // Adicionar anomalia à lista
    });

    eventSource.addEventListener('complete', (event) => {
      const results = JSON.parse(event.data);
      console.log('Investigação completa:', results);
      eventSource.close();
      // Atualizar estado com resultados finais
    });

    eventSource.onerror = () => {
      eventSource.close();
      console.error('Erro no streaming');
    };
  };

  // Listar investigações
  const loadInvestigations = async () => {
    const response = await fetch(`${API_BASE}/api/v1/investigations/`);
    const data = await response.json();
    setInvestigations(data);
  };

  // Carregar ao montar
  useEffect(() => {
    loadInvestigations();
  }, []);

  return {
    investigations,
    createInvestigation,
    loadInvestigations,
    isCreating
  };
}
```

### 11.4 Vue.js Composable

```typescript
// useCidadaoAPI.ts
import { ref, computed } from 'vue';

const API_BASE = 'https://cidadao-api-production.up.railway.app';

export function useCidadaoAPI() {
  const agents = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // Carregar agentes
  const loadAgents = async () => {
    isLoading.value = true;
    try {
      const response = await fetch(`${API_BASE}/api/v1/chat/agents`);
      agents.value = await response.json();
    } catch (e) {
      error.value = e.message;
    } finally {
      isLoading.value = false;
    }
  };

  // Enviar mensagem de chat
  const sendChatMessage = async (message: string, sessionId?: string) => {
    isLoading.value = true;
    try {
      const response = await fetch(`${API_BASE}/api/v1/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionId })
      });
      return await response.json();
    } catch (e) {
      error.value = e.message;
      throw e;
    } finally {
      isLoading.value = false;
    }
  };

  // Buscar dados do IBGE
  const getStates = async () => {
    const response = await fetch(`${API_BASE}/api/v1/federal/ibge/states`);
    const data = await response.json();
    return data.data;
  };

  const getMunicipalities = async (stateCode: string) => {
    const response = await fetch(
      `${API_BASE}/api/v1/federal/ibge/municipalities?state_code=${stateCode}`
    );
    const data = await response.json();
    return data.data;
  };

  return {
    agents,
    isLoading,
    error,
    loadAgents,
    sendChatMessage,
    getStates,
    getMunicipalities
  };
}
```

---

## 12. TRATAMENTO DE ERROS

### 12.1 Códigos de Status HTTP

| Código | Significado | Ação do Frontend |
|--------|-------------|------------------|
| **200** | OK | Processar resposta normalmente |
| **201** | Created | Recurso criado com sucesso |
| **204** | No Content | Operação bem-sucedida, sem conteúdo |
| **400** | Bad Request | Validar inputs do usuário |
| **401** | Unauthorized | Redirecionar para login |
| **403** | Forbidden | Mostrar "sem permissão" |
| **404** | Not Found | Mostrar "não encontrado" |
| **422** | Validation Error | Mostrar erros de validação |
| **429** | Rate Limited | Aguardar e tentar novamente |
| **500** | Server Error | Mostrar erro genérico |
| **503** | Service Unavailable | Mostrar "em manutenção" |

### 12.2 Estrutura de Erro Padrão

```typescript
interface APIError {
  status: "error";
  status_code: number;
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    field_errors?: Array<{
      field: string;
      message: string;
    }>;
  };
  request_id?: string;
}

// Exemplo de erro 422 (Validation)
{
  "status": "error",
  "status_code": 422,
  "error": {
    "code": "ValidationError",
    "message": "Invalid request data",
    "field_errors": [
      {
        "field": "query",
        "message": "Query must be at least 3 characters long"
      },
      {
        "field": "data_source",
        "message": "Invalid data source. Must be one of: contracts, expenses, ..."
      }
    ]
  },
  "request_id": "req_abc123"
}
```

### 12.3 Tratamento no Frontend

```typescript
// errorHandler.ts
export class APIError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export async function handleAPIResponse(response: Response) {
  if (!response.ok) {
    const errorData = await response.json();

    throw new APIError(
      response.status,
      errorData.error?.code || 'UnknownError',
      errorData.error?.message || 'An error occurred',
      errorData.error?.details
    );
  }

  return response.json();
}

// Uso
try {
  const data = await fetch(url).then(handleAPIResponse);
  // Processar data
} catch (error) {
  if (error instanceof APIError) {
    switch (error.statusCode) {
      case 401:
        redirectToLogin();
        break;
      case 422:
        showValidationErrors(error.details.field_errors);
        break;
      case 429:
        showRateLimitMessage();
        break;
      default:
        showGenericError(error.message);
    }
  }
}
```

### 12.4 Retry Logic

```typescript
async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  maxRetries = 3
): Promise<Response> {
  let lastError: Error;

  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);

      // Não fazer retry em erros do cliente (4xx)
      if (response.status >= 400 && response.status < 500) {
        return response;
      }

      // Fazer retry em erros do servidor (5xx)
      if (response.status >= 500) {
        throw new Error(`Server error: ${response.status}`);
      }

      return response;
    } catch (error) {
      lastError = error;

      // Esperar antes de tentar novamente (exponential backoff)
      if (i < maxRetries - 1) {
        await new Promise(resolve =>
          setTimeout(resolve, Math.pow(2, i) * 1000)
        );
      }
    }
  }

  throw lastError;
}
```

---

## 13. PERFORMANCE E OTIMIZAÇÃO

### 13.1 Caching no Frontend

```typescript
// SimpleCache.ts
class SimpleCache<T> {
  private cache = new Map<string, { data: T; expires: number }>();

  set(key: string, data: T, ttlSeconds = 300) {
    this.cache.set(key, {
      data,
      expires: Date.now() + ttlSeconds * 1000
    });
  }

  get(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() > entry.expires) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  clear() {
    this.cache.clear();
  }
}

// Uso
const apiCache = new SimpleCache();

async function getChatAgents() {
  const cacheKey = 'chat_agents';

  // Tentar cache primeiro
  const cached = apiCache.get(cacheKey);
  if (cached) return cached;

  // Buscar da API
  const response = await fetch(`${API_BASE}/api/v1/chat/agents`);
  const data = await response.json();

  // Armazenar em cache (5 minutos)
  apiCache.set(cacheKey, data, 300);

  return data;
}
```

### 13.2 Debouncing para Busca

```typescript
function useDebounce<T>(value: T, delay = 500): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// Uso em componente de busca
function SearchComponent() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  useEffect(() => {
    if (debouncedSearchTerm.length >= 3) {
      // Fazer busca na API
      searchAPI(debouncedSearchTerm);
    }
  }, [debouncedSearchTerm]);

  return (
    <input
      type="text"
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Buscar..."
    />
  );
}
```

### 13.3 Paginação

```typescript
interface PaginationParams {
  limit?: number;
  offset?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

async function getInvestigations(params: PaginationParams = {}) {
  const {
    limit = 20,
    offset = 0,
    sort_by = 'created_at',
    order = 'desc'
  } = params;

  const queryString = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
    sort_by,
    order
  });

  const response = await fetch(
    `${API_BASE}/api/v1/investigations/?${queryString}`
  );

  return response.json();
}

// Uso com infinite scroll
function InvestigationsList() {
  const [investigations, setInvestigations] = useState([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const loadMore = async () => {
    const data = await getInvestigations({ limit: 20, offset });

    setInvestigations(prev => [...prev, ...data]);
    setOffset(prev => prev + 20);
    setHasMore(data.length === 20);
  };

  // ... render com infinite scroll
}
```

### 13.4 Request Batching

```typescript
class RequestBatcher {
  private pending: Array<{
    resolve: (value: any) => void;
    reject: (error: any) => void;
  }> = [];
  private timer: NodeJS.Timeout | null = null;

  async batch(request: () => Promise<any>): Promise<any> {
    return new Promise((resolve, reject) => {
      this.pending.push({ resolve, reject });

      if (!this.timer) {
        this.timer = setTimeout(() => {
          this.flush(request);
        }, 50); // Aguardar 50ms para agrupar requests
      }
    });
  }

  private async flush(request: () => Promise<any>) {
    const requests = this.pending.splice(0);
    this.timer = null;

    try {
      const result = await request();
      requests.forEach(req => req.resolve(result));
    } catch (error) {
      requests.forEach(req => req.reject(error));
    }
  }
}
```

---

## 14. REFERÊNCIA RÁPIDA

### 14.1 URLs Base

```
Produção:  https://cidadao-api-production.up.railway.app
Local:     http://localhost:8000
Docs:      /docs
OpenAPI:   /openapi.json
```

### 14.2 Headers Comuns

```typescript
// JSON Request
{
  'Content-Type': 'application/json'
}

// Com autenticação
{
  'Content-Type': 'application/json',
  'Authorization': 'Bearer your-jwt-token'
}

// Com API Key
{
  'X-API-Key': 'your-api-key'
}
```

### 14.3 Endpoints Mais Usados

```typescript
// Chat
POST   /api/v1/chat/message
GET    /api/v1/chat/agents

// Investigações
POST   /api/v1/investigations/start
GET    /api/v1/investigations/
GET    /api/v1/investigations/{id}/results
GET    /api/v1/investigations/stream/{id}  // SSE

// Agentes
GET    /api/v1/agents/
GET    /api/v1/agents/status
POST   /api/v1/agents/{agent_name}

// Dados
GET    /api/v1/federal/ibge/states
GET    /api/v1/federal/ibge/municipalities

// Export
POST   /api/v1/export/investigations/{id}/download

// Health
GET    /health/
```

### 14.4 Tipos de Dados Importantes

```typescript
// Data Sources
"contracts" | "expenses" | "agreements" | "biddings" | "servants"

// Anomaly Types
"price" | "vendor" | "temporal" | "payment" | "duplicate" | "pattern"

// Severities
"low" | "medium" | "high" | "critical"

// Status
"pending" | "processing" | "completed" | "failed"

// Export Formats
"json" | "csv" | "excel" | "pdf"
```

### 14.5 Rate Limits

```
Free Tier:     60 requests/minute
Basic Tier:    300 requests/minute
Premium Tier:  1000 requests/minute

Header: X-RateLimit-Remaining
Header: X-RateLimit-Reset
```

---

## CONCLUSÃO

Este guia cobre **100% das funcionalidades** disponíveis no backend Cidadão.AI para integração frontend. Use como referência durante o desenvolvimento e consulte a documentação interativa em `/docs` para detalhes adicionais.

**Próximos Passos**:
1. Implementar cliente API com tipos TypeScript
2. Criar componentes React/Vue para chat
3. Implementar sistema de investigações
4. Adicionar visualizações de dados
5. Configurar SSE/WebSocket para tempo real

**Suporte**:
- Documentação: https://cidadao-api-production.up.railway.app/docs
- Issues: GitHub repository
- Email: andersonhs27@gmail.com

---

**Versão**: 1.0
**Última Atualização**: 2025-10-22
**Próxima Revisão**: 2025-11-22
