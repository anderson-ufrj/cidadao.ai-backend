# Cidadão.AI Backend API Data Structures

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

This document provides a comprehensive reference for all Pydantic models, request/response schemas, and data structures used in the Cidadão.AI backend API that a frontend application would need to implement.

## Table of Contents
1. [Chat API Models](#chat-api-models)
2. [WebSocket Models](#websocket-models)
3. [Investigation Models](#investigation-models)
4. [Authentication Models](#authentication-models)
5. [Agent Models](#agent-models)
6. [Pagination Models](#pagination-models)
7. [Error Response Format](#error-response-format)

---

## Chat API Models

### ChatRequest
```python
class ChatRequest(BaseModel):
    """Chat message request"""
    message: str  # min_length=1, max_length=1000
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
```

### ChatResponse
```python
class ChatResponse(BaseModel):
    """Chat message response"""
    session_id: str
    agent_id: str
    agent_name: str
    message: str
    confidence: float
    suggested_actions: Optional[List[str]] = None
    requires_input: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = {}
```

### QuickAction
```python
class QuickAction(BaseModel):
    """Quick action suggestion"""
    id: str
    label: str
    icon: str
    action: str
```

### Stream Response Format (SSE)
```javascript
// Server-Sent Events format for /api/v1/chat/stream
data: {"type": "start", "timestamp": "2025-01-19T12:00:00Z"}
data: {"type": "detecting", "message": "Analisando sua mensagem..."}
data: {"type": "intent", "intent": "investigate", "confidence": 0.92}
data: {"type": "agent_selected", "agent_id": "zumbi", "agent_name": "Zumbi dos Palmares"}
data: {"type": "chunk", "content": "Olá! Sou Zumbi dos Palmares..."}
data: {"type": "complete", "suggested_actions": ["start_investigation", "learn_more"]}
data: {"type": "error", "message": "Erro ao processar mensagem"}
```

---

## WebSocket Models

### WebSocketMessage
```python
class WebSocketMessage(BaseModel):
    """WebSocket message structure"""
    type: str  # Message type
    data: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    id: str = Field(default_factory=lambda: str(uuid4()))
```

### WebSocket Connection URL
```
ws://localhost:8000/api/v1/ws/chat/{session_id}?token={jwt_token}
```

### WebSocket Message Types

#### Client to Server
```javascript
// Send chat message
{
    "type": "chat_message",
    "data": {
        "message": "Investigar contratos do Ministério da Saúde",
        "context": {}
    }
}

// Subscribe to investigation
{
    "type": "subscribe_investigation",
    "data": {
        "investigation_id": "123e4567-e89b-12d3-a456-426614174000"
    }
}

// Unsubscribe from investigation
{
    "type": "unsubscribe_investigation",
    "data": {
        "investigation_id": "123e4567-e89b-12d3-a456-426614174000"
    }
}

// Keep alive ping
{
    "type": "ping",
    "data": {}
}
```

#### Server to Client
```javascript
// Connection established
{
    "type": "connection",
    "data": {
        "status": "connected",
        "session_id": "abc123",
        "message": "Conectado ao Cidadão.AI em tempo real"
    },
    "timestamp": "2025-01-19T12:00:00Z",
    "id": "msg123"
}

// Agent response
{
    "type": "agent_response",
    "data": {
        "agent_id": "zumbi",
        "agent_name": "Zumbi dos Palmares",
        "message": "Encontrei 15 anomalias nos contratos...",
        "confidence": 0.92,
        "metadata": {
            "processing_time_ms": 1250,
            "anomalies_found": 15
        }
    }
}

// Investigation update
{
    "type": "investigation_update",
    "data": {
        "investigation_id": "123e4567",
        "status": "processing",
        "progress": 0.75,
        "current_phase": "analyzing_patterns",
        "anomalies_detected": 12
    }
}

// Error message
{
    "type": "error",
    "data": {
        "code": "PROCESSING_ERROR",
        "message": "Failed to process request",
        "details": {}
    }
}

// Pong response
{
    "type": "pong",
    "data": {}
}
```

---

## Investigation Models

### InvestigationRequest
```python
class InvestigationRequest(BaseModel):
    """Request model for starting an investigation"""
    query: str  # Investigation query or focus area
    data_source: str = "contracts"  # One of: contracts, expenses, agreements, biddings, servants
    filters: Dict[str, Any] = {}
    anomaly_types: List[str] = ["price", "vendor", "temporal", "payment"]
    include_explanations: bool = True
    stream_results: bool = False
```

### InvestigationResponse
```python
class InvestigationResponse(BaseModel):
    """Response model for investigation results"""
    investigation_id: str
    status: str
    query: str
    data_source: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    anomalies_found: int
    total_records_analyzed: int
    results: List[Dict[str, Any]]
    summary: str
    confidence_score: float
    processing_time: float
```

### AnomalyResult
```python
class AnomalyResult(BaseModel):
    """Individual anomaly result"""
    anomaly_id: str
    type: str  # price, vendor, temporal, payment, duplicate, pattern
    severity: str  # low, medium, high, critical
    confidence: float
    description: str
    explanation: str
    affected_records: List[Dict[str, Any]]
    suggested_actions: List[str]
    metadata: Dict[str, Any]
```

### InvestigationStatus
```python
class InvestigationStatus(BaseModel):
    """Investigation status response"""
    investigation_id: str
    status: str  # started, processing, completed, failed
    progress: float  # 0.0 to 1.0
    current_phase: str
    records_processed: int
    anomalies_detected: int
    estimated_completion: Optional[datetime] = None
```

---

## Authentication Models

### LoginRequest
```python
class LoginRequest(BaseModel):
    email: str  # EmailStr
    password: str
```

### LoginResponse
```python
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: {
        "id": str,
        "email": str,
        "name": str,
        "role": str,
        "is_active": bool
    }
```

### RefreshRequest
```python
class RefreshRequest(BaseModel):
    refresh_token: str
```

### RefreshResponse
```python
class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
```

### RegisterRequest
```python
class RegisterRequest(BaseModel):
    email: str  # EmailStr
    password: str
    name: str
    role: Optional[str] = "analyst"
```

### UserResponse
```python
class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
```

### Authorization Header
```
Authorization: Bearer {access_token}
```

---

## Agent Models

### AgentMessage
```python
class AgentMessage(BaseModel):
    """Message passed between agents"""
    sender: str  # Agent that sent the message
    recipient: str  # Agent that should receive the message
    action: str  # Action to perform
    payload: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    timestamp: datetime
    message_id: str
    requires_response: bool = True
```

### AgentResponse
```python
class AgentResponse(BaseModel):
    """Response from an agent"""
    agent_name: str
    status: str  # IDLE, PROCESSING, COMPLETED, ERROR, REFLECTING
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}
    timestamp: datetime
    processing_time_ms: Optional[float] = None
```

### Available Agents
```javascript
const AGENTS = {
    abaporu: { name: "Abaporu", role: "Orquestrador" },
    zumbi: { name: "Zumbi dos Palmares", role: "Investigador" },
    anita: { name: "Anita Garibaldi", role: "Analista" },
    tiradentes: { name: "Tiradentes", role: "Relator" },
    machado: { name: "Machado de Assis", role: "Textual" },
    dandara: { name: "Dandara", role: "Justiça Social" },
    drummond: { name: "Carlos Drummond de Andrade", role: "Comunicação" }
}
```

---

## Pagination Models

### CursorPaginationRequest
```python
class CursorPaginationRequest(BaseModel):
    """Request parameters for cursor pagination"""
    cursor: Optional[str] = None  # Base64 encoded cursor
    limit: int = 20  # min=1, max=100
    direction: str = "next"  # next or prev
```

### CursorPaginationResponse
```python
class CursorPaginationResponse(BaseModel):
    """Response with cursor pagination metadata"""
    items: List[T]
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    has_more: bool = False
    total_items: Optional[int] = None
    metadata: Dict[str, Any] = {}
```

### Cursor Format
```javascript
// Cursor is base64 encoded JSON
{
    "t": "2025-01-19T12:00:00Z",  // timestamp
    "i": "123e4567",               // id
    "d": "next"                    // direction
}
```

---

## Error Response Format

All API errors follow this standardized format:

### HTTP Exception Response
```javascript
{
    "status": "error",
    "status_code": 400,  // HTTP status code
    "error": {
        "error": "HTTPException",
        "message": "Invalid request data",
        "details": {}
    }
}
```

### Application Error Response
```javascript
{
    "status": "error",
    "status_code": 500,
    "error": {
        "error": "InternalServerError",
        "message": "An unexpected error occurred",
        "details": {
            "error_type": "DatabaseConnectionError"  // Only in development
        }
    }
}
```

### Custom Exception Format (CidadaoAIError)
```javascript
{
    "error": "AgentExecutionError",  // Error code
    "message": "Agent failed to execute task",
    "details": {
        "agent": "zumbi",
        "action": "investigate",
        "error": "Connection timeout"
    }
}
```

---

## Common HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## API Base URLs

### Development
```
http://localhost:8000/api/v1
ws://localhost:8000/api/v1/ws
```

### Production (HuggingFace Spaces)
```
https://neural-thinker-cidadao-ai-backend.hf.space/api/v1
wss://neural-thinker-cidadao-ai-backend.hf.space/api/v1/ws
```

---

## TypeScript Interface Examples

For TypeScript frontend implementations, here are the equivalent interfaces:

```typescript
// Chat interfaces
interface ChatRequest {
    message: string;
    session_id?: string;
    context?: Record<string, any>;
}

interface ChatResponse {
    session_id: string;
    agent_id: string;
    agent_name: string;
    message: string;
    confidence: number;
    suggested_actions?: string[];
    requires_input?: Record<string, string>;
    metadata: Record<string, any>;
}

// WebSocket interfaces
interface WebSocketMessage {
    type: string;
    data: Record<string, any>;
    timestamp: string;
    id: string;
}

// Investigation interfaces
interface InvestigationRequest {
    query: string;
    data_source?: 'contracts' | 'expenses' | 'agreements' | 'biddings' | 'servants';
    filters?: Record<string, any>;
    anomaly_types?: string[];
    include_explanations?: boolean;
    stream_results?: boolean;
}

// Error interface
interface ErrorResponse {
    status: 'error';
    status_code: number;
    error: {
        error: string;
        message: string;
        details: Record<string, any>;
    };
}
```

---

## Notes for Frontend Developers

1. **Authentication**: All authenticated endpoints require the `Authorization: Bearer {token}` header
2. **WebSocket**: Connect with JWT token as query parameter for authentication
3. **Pagination**: Use cursor-based pagination for chat history and large datasets
4. **Error Handling**: Always check for error responses and handle appropriately
5. **SSE Streaming**: For real-time responses, use EventSource API with `/api/v1/chat/stream`
6. **Rate Limiting**: Respect rate limits indicated in response headers
7. **Timestamp Format**: All timestamps are in ISO 8601 format (UTC)
8. **IDs**: All entity IDs are UUIDs in string format
