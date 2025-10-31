# Chat Endpoints & Maritaca Integration Analysis
**Date**: 2025-10-22
**Status**: ✅ Verified and Documented

## Executive Summary

This document provides a comprehensive analysis of the chat endpoints and how they integrate with Maritaca AI (Sabiá-3 models) in the Cidadão.AI backend. The analysis was performed to help the frontend team understand what information is available and how to better utilize it.

---

## 📍 Chat Endpoints Overview

### Main Endpoints

#### 1. **POST /api/v1/chat/message**
Main endpoint for synchronous chat interactions.

**Location**: `src/api/routes/chat.py:119`

**Request**:
```python
{
    "message": str,              # User's message (1-1000 chars)
    "session_id": str | null,    # Optional session ID
    "context": dict | null       # Optional context data
}
```

**Response** (`ChatResponse`):
```python
{
    "session_id": str,                    # Session identifier
    "agent_id": str,                      # Which agent handled it
    "agent_name": str,                    # Agent's full name
    "message": str,                       # Response message
    "confidence": float,                  # 0.0-1.0 confidence score
    "suggested_actions": list[str],       # Action suggestions
    "requires_input": dict | null,        # If additional input needed
    "metadata": {
        "intent_type": str,               # Detected intent type
        "processing_time": float,         # Response time in seconds
        "is_demo_mode": bool,            # If user is authenticated
        "timestamp": str,                 # ISO timestamp
        "portal_data": {                  # If real data was fetched
            "type": str,                  # Data type
            "entities_found": dict,       # Extracted entities
            "total_records": int,         # Records count
            "has_data": bool             # If data exists
        }
    }
}
```

**Intent Types** (from `IntentDetector`):
- `GREETING` → Routes to Drummond
- `CONVERSATION` → Routes to Drummond
- `HELP_REQUEST` → Routes to Drummond
- `ABOUT_SYSTEM` → Routes to Drummond
- `SMALLTALK` → Routes to Drummond
- `THANKS` → Routes to Drummond
- `GOODBYE` → Routes to Drummond
- `INVESTIGATE` → Routes to Zumbi (with investigation flow)
- Other intents → Routes to Abaporu (master orchestrator)

#### 2. **POST /api/v1/chat/stream**
Server-Sent Events (SSE) streaming endpoint for real-time responses.

**Location**: `src/api/routes/chat.py:543`

**Event Types**:
```python
# 1. Start
{"type": "start", "timestamp": str}

# 2. Detecting
{"type": "detecting", "message": "Analisando sua mensagem..."}

# 3. Intent detected
{"type": "intent", "intent": str, "confidence": float}

# 4. Agent selected
{"type": "agent_selected", "agent_id": str, "agent_name": str}

# 5. Content chunks (streaming)
{"type": "chunk", "content": str}

# 6. Complete
{"type": "complete", "suggested_actions": list[str]}

# 7. Error
{"type": "error", "message": str}
```

#### 3. **GET /api/v1/chat/suggestions**
Quick action suggestions for the chat interface.

**Location**: `src/api/routes/chat.py:601`

**Response**:
```python
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
    },
    # ... more suggestions
]
```

#### 4. **GET /api/v1/chat/history/{session_id}**
Retrieve chat history for a session.

**Location**: `src/api/routes/chat.py:634`

**Response**:
```python
{
    "session_id": str,
    "messages": list[dict],              # Message history
    "total_messages": int,
    "current_investigation_id": str | null
}
```

#### 5. **GET /api/v1/chat/history/{session_id}/paginated**
Paginated chat history with cursor-based navigation.

**Location**: `src/api/routes/chat.py:657`

**Query Parameters**:
- `cursor`: Pagination cursor
- `limit`: Number of messages (max 100)
- `direction`: "next" or "prev"

#### 6. **GET /api/v1/chat/agents**
List all available chat agents.

**Location**: `src/api/routes/chat.py:737`

**Response**:
```python
[
    {
        "id": "abaporu",
        "name": "Abaporu",
        "avatar": "🎨",
        "role": "Orquestrador Master",
        "description": "Coordena investigações complexas",
        "status": "active"
    },
    # ... 6 agents total
]
```

---

## 🤖 Maritaca AI Integration

### Architecture

The system uses **Maritaca AI** (Brazilian Portuguese native models) as the primary LLM provider, with **Anthropic Claude** as a backup.

**Provider Configuration** (`.env`):
```bash
LLM_PROVIDER=maritaca                    # Current provider
MARITACA_API_KEY=<key>                   # Maritaca API key
MARITACA_MODEL=sabiazinho-3              # Model being used
ANTHROPIC_API_KEY=<key>                  # Backup provider
```

### Maritaca Client

**Location**: `src/services/maritaca_client.py`

**Available Models**:
- `sabiazinho-3` (💰 Most economical) - **CURRENTLY USED**
- `sabia-3`
- `sabia-3-medium`
- `sabia-3-large`

**Key Features**:
- ✅ Async/await throughout
- ✅ Automatic retry with exponential backoff
- ✅ Rate limit handling (429 errors)
- ✅ Circuit breaker pattern (fails after 5 consecutive errors)
- ✅ Streaming support
- ✅ Comprehensive logging
- ✅ Request/response tracking

**Response Structure** (`MaritacaResponse`):
```python
{
    "content": str,                      # Generated text
    "model": str,                        # Model used
    "usage": {                           # Token usage
        "prompt_tokens": int,
        "completion_tokens": int,
        "total_tokens": int
    },
    "metadata": {
        "id": str,                       # Request ID
        "created": int,                  # Unix timestamp
        "object": str                    # Response type
    },
    "response_time": float,              # Response time in seconds
    "timestamp": datetime,               # Python datetime
    "finish_reason": str                 # Why it stopped
}
```

### Drummond Agent (Conversational AI)

**Location**: `src/agents/drummond.py`

**Initialization** (line 283):
```python
def _init_llm_client(self):
    api_key = os.environ.get("MARITACA_API_KEY")
    if api_key:
        self.llm_client = MaritacaClient(
            api_key=api_key,
            model=MaritacaModel.SABIAZINHO_3,  # Economical model
            timeout=30,
        )
```

**Personality Prompt** (line 275):
```python
self.personality_prompt = """Você é Carlos Drummond de Andrade, poeta mineiro e assistente do Cidadão.AI.

ESTILO: Clareza poética, ironia mineira sutil, empatia genuína.
FALA: Saudações mineiras ("Uai!"), metáforas do cotidiano brasileiro.
FOCO: Transparência governamental em linguagem acessível.
CAPACIDADES: Posso conversar e orientar. Para investigações específicas, sugiro: "quero investigar contratos de saúde" ou "verificar salários de servidores".
LEMBRE: "No meio do caminho tinha uma pedra" - vá direto ao essencial."""
```

**Conversation Processing** (line 867):
```python
async def generate_contextual_response(
    self, message: str, context: ConversationContext
) -> dict[str, str]:
    """Gera resposta contextual usando Maritaca."""

    if self.llm_client:
        # Build conversation history
        messages = [
            MaritacaMessage(role="system", content=self.personality_prompt)
        ]

        # Add recent messages (last 5)
        history = await self.conversational_memory.get_recent_messages(
            context.session_id, limit=5
        )
        for msg in history:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append(MaritacaMessage(role=role, content=msg["content"]))

        # Add current message
        messages.append(MaritacaMessage(role="user", content=message))

        # Generate response with Sabiazinho-3
        response = await self.llm_client.chat(
            messages=messages,
            temperature=0.7,        # Creativity level
            max_tokens=300,         # Reduced to save credits
        )

        return {
            "content": response.content.strip(),
            "metadata": {
                "type": "contextual",
                "llm_model": response.model,      # Which model was used
                "usage": response.usage,          # Token consumption
            },
        }
```

### Response Metadata Available to Frontend

From the Maritaca integration, the following metadata is **already being returned** but may not be fully utilized by the frontend:

```python
{
    "metadata": {
        "type": "contextual",                # Response type
        "llm_model": "sabiazinho-3",        # Model that generated it
        "usage": {                           # ⭐ TOKEN USAGE INFO
            "prompt_tokens": 150,            # Tokens in prompt
            "completion_tokens": 75,         # Tokens in response
            "total_tokens": 225              # Total consumed
        }
    }
}
```

---

## 🎯 What the Frontend Can Leverage

### 1. **Token Usage Tracking**
The `usage` object in metadata contains:
- `prompt_tokens`: Context sent to LLM
- `completion_tokens`: Response generated
- `total_tokens`: Total API consumption

**Potential Frontend Uses**:
- Display token usage to user
- Show cost estimation (if prices known)
- Implement usage warnings
- Track conversation efficiency

### 2. **Model Information**
The `llm_model` field shows which model was used:
- `sabiazinho-3`: Current economical model
- Future: Could switch to larger models for complex queries

**Potential Frontend Uses**:
- Show model badge on responses
- Indicate when using more powerful models
- Explain response quality/speed trade-offs

### 3. **Response Type Classification**
The `type` field in metadata indicates:
- `contextual`: LLM-generated with context
- `fallback`: Template-based (LLM failed)
- `system_explanation`: Hardcoded system info
- `help`: Contextual help response

**Potential Frontend Uses**:
- Style different response types differently
- Show indicators for AI vs template responses
- Highlight when LLM is unavailable

### 4. **Processing Time**
Available in `metadata.processing_time`:

**Potential Frontend Uses**:
- Show loading indicators with estimated time
- Display response generation time
- Identify slow queries for optimization

### 5. **Confidence Scores**
All responses include a `confidence` field (0.0-1.0):

**Potential Frontend Uses**:
- Visual confidence indicator
- Warning on low confidence (<0.5)
- Suggest rephrasing for low confidence
- Alternative actions on uncertainty

### 6. **Suggested Actions**
Dynamic action suggestions based on context:

**Current Implementation**:
```python
# For investigations (src/api/routes/chat.py:358)
if investigation_result["anomalies_found"] > 0:
    suggested_actions = [
        "🔍 Ver detalhes das anomalias",
        "📊 Gerar relatório completo",
        "📂 Explorar dados abertos relacionados"
    ]
```

**Potential Improvements**:
- Make actions clickable with structured data
- Include action IDs for programmatic handling
- Add action metadata (type, requires_auth, etc.)

---

## 🚀 Recommendations for Frontend Improvements

### 1. **Enhanced Response Display**

```typescript
// Current (simple)
<div className="message">{response.message}</div>

// Improved
<div className="message">
  <div className="content">{response.message}</div>

  {/* Show model info */}
  <div className="metadata">
    <span className="model-badge">
      {response.metadata.llm_model}
    </span>

    {/* Confidence indicator */}
    <ConfidenceBar value={response.confidence} />

    {/* Token usage */}
    <span className="tokens">
      {response.metadata.usage?.total_tokens} tokens
    </span>
  </div>

  {/* Suggested actions as buttons */}
  <div className="actions">
    {response.suggested_actions?.map(action => (
      <ActionButton key={action} label={action} />
    ))}
  </div>
</div>
```

### 2. **Smart Loading States**

```typescript
// Show different messages based on intent
const loadingMessages = {
  'INVESTIGATE': 'Consultando bases de dados...',
  'ANALYZE': 'Analisando padrões...',
  'CONVERSATION': 'Pensando...',
};

<LoadingIndicator
  message={loadingMessages[intent.type]}
  processingTime={metadata.processing_time}
/>
```

### 3. **Token Usage Dashboard**

```typescript
// Track and display token consumption
const SessionStats = () => {
  const totalTokens = messages.reduce(
    (sum, msg) => sum + (msg.metadata?.usage?.total_tokens || 0),
    0
  );

  return (
    <div className="stats">
      <h4>Uso de Recursos</h4>
      <p>Total de tokens: {totalTokens.toLocaleString()}</p>
      <p>Custo estimado: R$ {(totalTokens * 0.0001).toFixed(4)}</p>
    </div>
  );
};
```

### 4. **Confidence-Based UI Feedback**

```typescript
const ConfidenceIndicator = ({ confidence }: { confidence: number }) => {
  if (confidence < 0.5) {
    return (
      <Alert severity="warning">
        Resposta com baixa confiança. Tente reformular sua pergunta.
      </Alert>
    );
  }

  if (confidence < 0.7) {
    return (
      <Tooltip title="Resposta moderadamente confiável">
        <InfoIcon color="info" />
      </Tooltip>
    );
  }

  return null; // High confidence, no indicator needed
};
```

### 5. **Investigation Status Tracking**

```typescript
// Use investigation metadata from Zumbi responses
interface InvestigationSummary {
  anomalies_found: number;
  records_analyzed: number;
  open_data_available: boolean;
  datasets_count: number;
}

const InvestigationCard = ({ summary }: { summary: InvestigationSummary }) => (
  <Card>
    <Stat label="Anomalias" value={summary.anomalies_found} color="red" />
    <Stat label="Registros" value={summary.records_analyzed} />
    <Stat label="Datasets" value={summary.datasets_count} />
    {summary.open_data_available && (
      <Badge>Dados Abertos Disponíveis</Badge>
    )}
  </Card>
);
```

---

## 📊 Data Flow Diagram

```
┌─────────────┐
│   Frontend  │
│   (Next.js) │
└──────┬──────┘
       │ POST /api/v1/chat/message
       │ { message, session_id, context }
       ▼
┌─────────────────────────────────────┐
│     Chat Router                      │
│     (src/api/routes/chat.py)        │
├─────────────────────────────────────┤
│ 1. Intent Detection                 │
│    └─> IntentDetector               │
│                                      │
│ 2. Portal da Transparência Check    │
│    └─> chat_data_integration        │
│                                      │
│ 3. Agent Routing                    │
│    ├─> Drummond (conversation)      │
│    ├─> Zumbi (investigation)        │
│    └─> Abaporu (orchestration)      │
└──────┬──────────────────────────────┘
       │
       ▼ (If Drummond)
┌─────────────────────────────────────┐
│   Drummond Agent                     │
│   (src/agents/drummond.py)          │
├─────────────────────────────────────┤
│ 1. Load conversation history (5)    │
│                                      │
│ 2. Build message context            │
│    ├─> System: personality_prompt   │
│    ├─> History: last 5 messages     │
│    └─> User: current message        │
│                                      │
│ 3. Call Maritaca AI                 │
│    └─> MaritacaClient               │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   Maritaca Client                    │
│   (src/services/maritaca_client.py) │
├─────────────────────────────────────┤
│ POST /chat/completions              │
│ {                                    │
│   "messages": [...],                │
│   "model": "sabiazinho-3",          │
│   "temperature": 0.7,               │
│   "max_tokens": 300                 │
│ }                                    │
└──────┬──────────────────────────────┘
       │
       ▼ (Maritaca API Response)
┌─────────────────────────────────────┐
│   {                                  │
│     "choices": [{                   │
│       "message": {                  │
│         "content": "Olá, uai!..."   │
│       },                            │
│       "finish_reason": "stop"       │
│     }],                             │
│     "usage": {                      │
│       "prompt_tokens": 150,         │
│       "completion_tokens": 75,      │
│       "total_tokens": 225           │
│     },                              │
│     "model": "sabiazinho-3"         │
│   }                                  │
└──────┬──────────────────────────────┘
       │
       ▼ (Transform to MaritacaResponse)
┌─────────────────────────────────────┐
│   MaritacaResponse                   │
│   {                                  │
│     content: "Olá, uai!...",        │
│     model: "sabiazinho-3",          │
│     usage: {...},                   │
│     metadata: {...},                │
│     response_time: 1.23,            │
│     timestamp: datetime,            │
│     finish_reason: "stop"           │
│   }                                  │
└──────┬──────────────────────────────┘
       │
       ▼ (Back to Drummond)
┌─────────────────────────────────────┐
│   Save to conversational memory     │
│   Build AgentResponse               │
│   {                                  │
│     agent_name: "drummond",         │
│     status: "COMPLETED",            │
│     result: {                       │
│       message: "Olá, uai!...",      │
│       metadata: {                   │
│         type: "contextual",         │
│         llm_model: "sabiazinho-3",  │
│         usage: {...}                │
│       }                             │
│     }                                │
│   }                                  │
└──────┬──────────────────────────────┘
       │
       ▼ (Back to Chat Router)
┌─────────────────────────────────────┐
│   Transform to ChatResponse         │
│   {                                  │
│     session_id: "...",              │
│     agent_id: "drummond",           │
│     agent_name: "Carlos Drummond...",│
│     message: "Olá, uai!...",        │
│     confidence: 0.95,               │
│     suggested_actions: [],          │
│     metadata: {                     │
│       intent_type: "GREETING",      │
│       processing_time: 1.5,         │
│       is_demo_mode: false,          │
│       timestamp: "2025-10-22..."    │
│     }                                │
│   }                                  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Frontend  │
│   Displays  │
└─────────────┘
```

---

## 🐛 Current Limitations

### 1. **Limited Metadata Exposure**
**Issue**: Rich metadata from Maritaca (token usage, model info) is available but not fully structured for frontend.

**Impact**: Frontend can't show token usage, model information, or cost estimates.

**Solution**: Already available in `response.metadata` - frontend just needs to display it!

### 2. **No Streaming Metadata**
**Issue**: SSE streaming endpoint doesn't send metadata chunks.

**Impact**: Frontend can't show real-time token consumption or model info during streaming.

**Recommendation**: Add metadata events to streaming:
```python
# In generate() function (chat.py:549)
yield f"data: {json.dumps({'type': 'metadata', 'llm_model': 'sabiazinho-3', 'tokens_used': 150})}\n\n"
```

### 3. **Suggested Actions Not Structured**
**Issue**: Actions are just strings, not structured objects.

**Impact**: Frontend must parse strings to make them interactive.

**Recommendation**: Return structured actions:
```python
# Instead of:
suggested_actions = ["🔍 Ver detalhes das anomalias"]

# Return:
suggested_actions = [{
    "id": "view_anomalies",
    "type": "navigation",
    "label": "Ver detalhes das anomalias",
    "icon": "search",
    "data": {"investigation_id": "..."}
}]
```

### 4. **No Cost Estimation**
**Issue**: Token usage is tracked but not converted to cost.

**Impact**: Users/admins can't track spending.

**Recommendation**: Add pricing info:
```python
MARITACA_PRICING = {
    "sabiazinho-3": {"input": 0.0001, "output": 0.0002},  # Per token
}

# In response metadata:
metadata["cost_estimate"] = {
    "input_cost": usage["prompt_tokens"] * MARITACA_PRICING[model]["input"],
    "output_cost": usage["completion_tokens"] * MARITACA_PRICING[model]["output"],
    "total_cost": ...,
    "currency": "BRL"
}
```

### 5. **No Conversation Analytics**
**Issue**: No aggregated stats on conversation quality/efficiency.

**Impact**: Can't optimize prompts or detect issues.

**Recommendation**: Add session-level analytics:
```python
# New endpoint: GET /api/v1/chat/analytics/{session_id}
{
    "total_messages": 20,
    "total_tokens": 5000,
    "total_cost": 0.50,
    "avg_confidence": 0.85,
    "avg_response_time": 1.2,
    "intents_breakdown": {
        "GREETING": 2,
        "INVESTIGATE": 5,
        "CONVERSATION": 13
    },
    "agents_used": {
        "drummond": 15,
        "zumbi": 5
    }
}
```

---

## ✅ Quick Wins for Frontend

### Immediate (No Backend Changes)

1. **Display Confidence Scores**
   - Already in `response.confidence`
   - Add visual indicator (color, icon, bar)

2. **Show Token Usage**
   - Already in `response.metadata.usage`
   - Display in dev mode or admin panel

3. **Better Action Buttons**
   - Parse `suggested_actions` strings
   - Make them clickable/interactive

4. **Model Badge**
   - Show `response.metadata.llm_model`
   - Help users understand response source

5. **Processing Time Feedback**
   - Use `response.metadata.processing_time`
   - Show "Responded in 1.5s"

### Short-term (Minor Backend Updates)

1. **Structured Actions**
   - Update action format to objects
   - Include action metadata (type, data)

2. **Cost Tracking**
   - Add pricing calculations
   - Return cost estimates in metadata

3. **Streaming Metadata**
   - Send metadata events in SSE
   - Real-time token/cost updates

---

## 📝 Summary

### What's Already Available ✅

- ✅ Token usage tracking (`metadata.usage`)
- ✅ Model information (`metadata.llm_model`)
- ✅ Confidence scores (`confidence`)
- ✅ Processing time (`metadata.processing_time`)
- ✅ Intent classification (`metadata.intent_type`)
- ✅ Suggested actions (as strings)
- ✅ Portal da Transparência integration metadata
- ✅ Investigation summaries (for Zumbi responses)

### What Could Be Improved 🔄

- 🔄 Structured action objects (instead of strings)
- 🔄 Cost estimation based on token usage
- 🔄 Streaming metadata events (SSE)
- 🔄 Conversation analytics aggregation
- 🔄 Better error messages with recovery suggestions

### Key Takeaway 💡

**The backend is already providing rich metadata** - the frontend just needs to display it effectively! Most improvements can happen on the frontend without any backend changes. The information is there, waiting to be used.

---

## 📚 Related Documentation

- Maritaca Client: `src/services/maritaca_client.py`
- Drummond Agent: `src/agents/drummond.py`
- Chat Routes: `src/api/routes/chat.py`
- Intent Detection: `src/services/chat_service.py`
- Agent Pool: `src/infrastructure/agent_pool.py`

---

**End of Analysis** | Last Updated: 2025-10-22
