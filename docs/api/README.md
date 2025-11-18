# 📡 API Documentation - Cidadão.AI

**Author**: Anderson Henrique da Silva
**Location**: Minas Gerais, Brazil
**Created**: 2025-09-25
**Last Updated**: 2025-11-18

[English version below](#-api-documentation---cidadãoai-english)

## 🌐 Visão Geral

API RESTful para análise de transparência governamental com sistema multi-agente de IA.

**Base URL**: `https://api.cidadao.ai` (produção) ou `http://localhost:8000` (desenvolvimento)

## 🔐 Autenticação

### JWT Bearer Token

```http
Authorization: Bearer <token>
```

### Obter Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "senha123"
}
```

**Resposta**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## 💬 Chat API

### Enviar Mensagem

```http
POST /api/v1/chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Quero investigar contratos do Ministério da Saúde",
  "session_id": "uuid-da-sessao"
}
```

**Resposta**:
```json
{
  "response": "Vou analisar os contratos do Ministério da Saúde...",
  "session_id": "uuid-da-sessao",
  "agent": "zumbi",
  "intent": "investigate",
  "metadata": {
    "processing_time": 1.23,
    "cache_hit": false,
    "timestamp": "2025-09-25T18:20:00Z"
  }
}
```

### Streaming de Resposta (SSE)

```http
POST /api/v1/chat/stream
Authorization: Bearer <token>
Content-Type: application/json
Accept: text/event-stream

{
  "message": "Analise detalhada dos gastos",
  "session_id": "uuid-da-sessao"
}
```

**Resposta** (Server-Sent Events):
```
data: {"chunk": "Iniciando análise", "type": "start"}

data: {"chunk": "Encontrei 15 contratos", "type": "progress"}

data: {"chunk": "Análise completa", "type": "complete"}
```

### Histórico de Conversa

```http
GET /api/v1/chat/history/{session_id}/paginated?cursor=&limit=20
Authorization: Bearer <token>
```

**Resposta**:
```json
{
  "messages": [
    {
      "id": "msg-uuid",
      "role": "user",
      "content": "Olá",
      "timestamp": "2025-09-25T18:00:00Z"
    },
    {
      "id": "msg-uuid-2",
      "role": "assistant",
      "content": "Olá! Como posso ajudar?",
      "timestamp": "2025-09-25T18:00:01Z",
      "agent": "drummond"
    }
  ],
  "next_cursor": "eyJpZCI6ICJtc2ctdXVpZC0zIn0=",
  "has_more": true
}
```

## 🔍 Investigações

### Criar Investigação

```http
POST /api/v1/investigations/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Análise de Contratos 2025",
  "description": "Investigar anomalias em contratos",
  "target_type": "contract",
  "parameters": {
    "org_code": "26000",
    "date_start": "2025-01-01",
    "date_end": "2025-09-25"
  }
}
```

**Resposta**:
```json
{
  "investigation_id": "inv-uuid",
  "status": "processing",
  "created_at": "2025-09-25T18:20:00Z",
  "estimated_time": 30
}
```

### Status da Investigação

```http
GET /api/v1/investigations/{investigation_id}
Authorization: Bearer <token>
```

**Resposta**:
```json
{
  "id": "inv-uuid",
  "status": "completed",
  "progress": 100,
  "results": {
    "anomalies_found": 5,
    "risk_score": 0.72,
    "summary": "Encontradas 5 anomalias significativas",
    "details": [...]
  },
  "created_at": "2025-09-25T18:20:00Z",
  "completed_at": "2025-09-25T18:25:00Z"
}
```

## 🤖 Agentes

### Listar Agentes Disponíveis

```http
GET /api/v1/agents/status
Authorization: Bearer <token>
```

**Resposta**:
```json
{
  "agents": [
    {
      "name": "zumbi",
      "display_name": "Zumbi dos Palmares",
      "role": "Investigador de Anomalias",
      "status": "operational",
      "capabilities": ["anomaly_detection", "pattern_analysis"],
      "load": 0.45
    },
    {
      "name": "anita",
      "display_name": "Anita Garibaldi",
      "role": "Analista de Padrões",
      "status": "operational",
      "capabilities": ["trend_analysis", "correlation"],
      "load": 0.32
    }
  ]
}
```

### Análise Direta com Agente

```http
POST /api/agents/zumbi
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "analyze_contracts",
  "data": {
    "contracts": [...],
    "threshold": 2.5
  }
}
```

## 📊 Portal da Transparência

### Buscar Contratos

```http
GET /api/v1/transparency/contracts?codigoOrgao=26000&pagina=1
Authorization: Bearer <token>
```

**Resposta**:
```json
{
  "contratos": [
    {
      "numero": "01/2025",
      "fornecedor": "Empresa XYZ",
      "valor": 150000.00,
      "dataAssinatura": "2025-01-15",
      "objeto": "Serviços de TI"
    }
  ],
  "total": 150,
  "pagina": 1,
  "totalPaginas": 15
}
```

### Buscar Servidor Público

```http
GET /api/v1/transparency/servants?cpf=***.680.938-**
Authorization: Bearer <token>
```

**Resposta**:
```json
{
  "servidor": {
    "nome": "FULANO DE TAL",
    "cargo": "Analista",
    "orgao": "Ministério XYZ",
    "situacao": "Ativo"
  }
}
```

## 📈 Monitoramento

### Health Check

```http
GET /health
```

**Resposta**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-09-25T18:20:00Z"
}
```

### Métricas Detalhadas

```http
GET /health/detailed
Authorization: Bearer <token>
```

**Resposta**:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "redis": "connected",
    "agents": "operational"
  },
  "metrics": {
    "uptime_seconds": 86400,
    "total_requests": 15000,
    "active_investigations": 12,
    "cache_hit_rate": 0.92
  }
}
```

## 🚨 Códigos de Erro

| Código | Descrição | Exemplo |
|--------|-----------|---------|
| 400 | Bad Request | Parâmetros inválidos |
| 401 | Unauthorized | Token inválido ou expirado |
| 403 | Forbidden | Sem permissão para o recurso |
| 404 | Not Found | Recurso não encontrado |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Erro do servidor |

### Formato de Erro

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "O parâmetro 'codigoOrgao' é obrigatório",
    "details": {
      "field": "codigoOrgao",
      "requirement": "string, 5 digits"
    }
  },
  "timestamp": "2025-09-25T18:20:00Z"
}
```

## ⚡ Rate Limiting

| Tier | Limite | Janela |
|------|--------|--------|
| Anônimo | 10 req | 1 min |
| Autenticado | 60 req | 1 min |
| Premium | 300 req | 1 min |
| Admin | Ilimitado | - |

Headers de resposta:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1632582000
```

## 🔄 WebSocket

### Chat em Tempo Real

```javascript
const ws = new WebSocket('wss://api.cidadao.ai/api/v1/ws/chat/{session_id}');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'message',
    content: 'Olá!'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Resposta:', data);
};
```

---

# 📡 API Documentation - Cidadão.AI (English)

**Author**: Anderson Henrique da Silva
**Last Updated**: 2025-09-25 18:20:00 -03:00 (São Paulo, Brazil)

## 🌐 Overview

RESTful API for government transparency analysis with multi-agent AI system.

**Base URL**: `https://api.cidadao.ai` (production) or `http://localhost:8000` (development)

## 🔐 Authentication

### JWT Bearer Token

```http
Authorization: Bearer <token>
```

### Get Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

[Continue with English translations of all sections above...]
