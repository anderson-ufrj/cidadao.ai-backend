# 💬 Chat API Documentation

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

**Status**: ✅ Implementado e Funcional
**Versão**: 1.0.0
**Data**: Setembro 2025

## 📋 Visão Geral

A API de Chat do Cidadão.AI permite interação conversacional natural com os agentes de IA para investigar contratos públicos, detectar anomalias e gerar relatórios.

## 🚀 Endpoints

### 1. Enviar Mensagem
```http
POST /api/v1/chat/message
```

Processa uma mensagem do usuário e retorna resposta do agente apropriado.

**Request Body:**
```json
{
  "message": "Quero investigar contratos do Ministério da Saúde",
  "session_id": "uuid-opcional",
  "context": {
    "additional": "data"
  }
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "abaporu",
  "agent_name": "Abaporu",
  "message": "Vou coordenar essa investigação. Qual período você gostaria de analisar?",
  "confidence": 0.85,
  "suggested_actions": ["start_investigation", "view_examples"],
  "requires_input": {
    "period": "Informe o período desejado"
  },
  "metadata": {
    "intent_type": "investigate",
    "processing_time": 0.234,
    "is_demo_mode": false,
    "timestamp": "2025-09-16T10:30:00Z"
  }
}
```

### 2. Stream de Mensagens (SSE)
```http
POST /api/v1/chat/stream
```

Retorna resposta em streaming usando Server-Sent Events para experiência mais fluida.

**Request Body:** Igual ao endpoint `/message`

**Response Stream:**
```
data: {"type": "start", "timestamp": "2025-01-16T10:30:00Z"}

data: {"type": "detecting", "message": "Analisando sua mensagem..."}

data: {"type": "intent", "intent": "investigate", "confidence": 0.85}

data: {"type": "agent_selected", "agent_id": "zumbi", "agent_name": "Zumbi dos Palmares"}

data: {"type": "chunk", "content": "Detectei que você quer"}

data: {"type": "chunk", "content": "investigar contratos..."}

data: {"type": "complete", "suggested_actions": ["start_investigation"]}
```

### 3. Sugestões Rápidas
```http
GET /api/v1/chat/suggestions
```

Retorna sugestões de perguntas/ações rápidas.

**Response:**
```json
[
  {
    "id": "investigate",
    "label": "Investigar contratos",
    "icon": "search",
    "action": "Quero investigar contratos do Ministério da Saúde"
  },
  {
    "id": "anomalies",
    "label": "Ver anomalias recentes",
    "icon": "alert-circle",
    "action": "Mostre as principais anomalias detectadas"
  }
]
```

### 4. Histórico de Chat
```http
GET /api/v1/chat/history/{session_id}?limit=50
```

Recupera histórico de mensagens de uma sessão.

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "user",
      "content": "Investigar contratos",
      "timestamp": "2025-09-16T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Vou coordenar essa investigação...",
      "timestamp": "2025-09-16T10:30:05Z",
      "agent_id": "abaporu"
    }
  ],
  "total_messages": 2,
  "current_investigation_id": "INV-2025-001"
}
```

### 5. Limpar Histórico
```http
DELETE /api/v1/chat/history/{session_id}
```

Limpa o histórico de uma sessão.

**Response:**
```json
{
  "message": "Histórico limpo com sucesso"
}
```

### 6. Listar Agentes
```http
GET /api/v1/chat/agents
```

Lista todos os agentes disponíveis para conversa.

**Response:**
```json
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
  }
]
```

## 🧠 Sistema de Detecção de Intenção

O sistema detecta automaticamente a intenção do usuário:

### Tipos de Intenção
- **INVESTIGATE**: Investigar contratos/gastos
- **ANALYZE**: Analisar anomalias/padrões
- **REPORT**: Gerar relatórios/documentos
- **STATUS**: Verificar status/progresso
- **HELP**: Ajuda/explicações
- **GREETING**: Saudações
- **QUESTION**: Perguntas gerais

### Extração de Entidades
- **Órgãos**: Ministério da Saúde (26000), Educação (25000), etc.
- **Períodos**: Anos, meses, períodos relativos
- **Valores**: Valores monetários em R$

### Roteamento de Agentes
```
INVESTIGATE → Abaporu (Master)
ANALYZE → Anita (Analyst)
REPORT → Tiradentes (Reporter)
QUESTION → Machado (Textual)
DEFAULT → Abaporu
```

## 💡 Exemplos de Uso

### Investigação Completa
```
USER: "Quero investigar contratos suspeitos"
BOT: "Qual órgão você gostaria de investigar?"
USER: "Ministério da Saúde"
BOT: "Qual período?"
USER: "Últimos 6 meses"
BOT: "Iniciando investigação..." [Cria investigação]
```

### Consulta Direta
```
USER: "Mostre anomalias do ministério da educação em 2024"
BOT: [Detecta órgão e período] "Analisando contratos..."
```

### Geração de Relatório
```
USER: "Gere um relatório da última investigação"
BOT: "Gerando relatório em PDF..." [Link para download]
```

## 🔧 Configuração

### Headers Necessários
```
Content-Type: application/json
Authorization: Bearer {token} (opcional)
```

### Parâmetros de Sessão
- Sessões expiram após 24 horas de inatividade
- Máximo 1000 mensagens por sessão
- Cache de 5 minutos para respostas idênticas

## 🎯 Boas Práticas

1. **Mantenha sessões**: Use o mesmo `session_id` para contexto
2. **Mensagens claras**: Seja específico sobre órgãos e períodos
3. **Use sugestões**: Aproveite as sugestões rápidas
4. **Streaming para UX**: Use `/stream` para experiência fluida

## 🚨 Limitações

- Mensagens: Máximo 1000 caracteres
- Rate limit: 60 mensagens/minuto por IP
- Sessões: Máximo 100 ativas por usuário
- Histórico: Últimas 1000 mensagens

## 🔐 Segurança

- Autenticação JWT opcional
- Sanitização de entrada
- Proteção contra XSS
- Rate limiting por IP/usuário

---

**Próximo**: [Integração Frontend](./FRONTEND_CHATBOT_PROMPT.md)
